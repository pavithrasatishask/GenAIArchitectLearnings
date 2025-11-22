# ingest_to_pgvector.py
"""
Ingestion script:
- Reads PDF pages (pdfplumber wrapper in ingest.pdf_ingest)
- Collects page text + image OCR text
- Normalizes and chunks text
- Generates embeddings in batches (via ingest.embedder.embed_texts)
- Upserts embeddings into Neon pgvector (db.pgvector_store.upsert_embedding)
- Creates simple Neo4j Page nodes (kg.neo4j_client.create_page_node)
"""

import os
import math
import time
import hashlib
from dotenv import load_dotenv

load_dotenv()

from ingest.pdf_ingest import extract_pages, normalize_text
from ingest.chunker import chunk_text
from ingest.embedder import embed_texts
from db.pgvector_store import initialize_schema, upsert_embedding
from kg.neo4j_client import get_driver, create_page_node

# Config (override by environment)
PDF_PATH = os.getenv("PDF_PATH", "data/tamil_grade8_book.pdf")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", 8))
SLEEP_BETWEEN_BATCHES = float(os.getenv("SLEEP_BETWEEN_BATCHES", 0.2))

def chunk_id_for(page, idx):
    """Deterministic chunk id from page & chunk index."""
    key = f"{page}-{idx}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def prepare_chunks_from_pages(pages):
    """
    pages: output from extract_pages()
    returns: list of chunk dicts:
      {"chunk_id","text","page","source","metadata"}
    """
    all_chunks = []
    for p in pages:
        page_num = p.get("page")
        # base text from selectable text or full-page OCR
        text = p.get("text", "") or ""
        # incorporate OCR text from any embedded images (if present)
        images = p.get("images", []) or []
        for im in images:
            ocr_block = im.get("ocr")
            if isinstance(ocr_block, dict):
                img_text = ocr_block.get("text", "")
                if img_text:
                    text += "\n" + img_text

        # Normalize
        text = normalize_text(text)

        if not text.strip():
            continue

        # Chunk the text
        chunks = chunk_text(text)
        for i, ch in enumerate(chunks):
            cid = chunk_id_for(page_num, i)
            metadata = {"page": page_num, "source": "TamilBook", "chunk_index": i, "text_len": len(ch["text"])}
            all_chunks.append({
                "chunk_id": cid,
                "text": ch["text"],
                "page": page_num,
                "source": "TamilBook",
                "metadata": metadata
            })

    return all_chunks


def batch(iterable, n=1):
    """Simple batching helper."""
    l = len(iterable)
    for i in range(0, l, n):
        yield iterable[i:i + n]


def upsert_chunks_with_embeddings(chunks):
    """
    Given list of chunk dicts, obtain embeddings in batches and upsert each to DB.
    Also create basic Neo4j Page nodes (one per page).
    """
    if not chunks:
        print("No chunks to upsert.")
        return

    # initialize DB schema (creates extension/table/index if not exists)
    initialize_schema()

    # group by page to make page node creation idempotent
    pages_seen = set()

    texts = [c["text"] for c in chunks]
    total = len(texts)
    steps = math.ceil(total / EMBED_BATCH_SIZE)
    print(f"Total chunks: {total}, batch size: {EMBED_BATCH_SIZE}, batches: {steps}")

    index = 0
    for batch_texts in batch(texts, EMBED_BATCH_SIZE):
        # Get embeddings for this batch
        try:
            vectors = embed_texts(batch_texts)
        except Exception as e:
            print(f"[ERROR] Embedding API failed at batch starting index {index}: {e}")
            # try simple retry once
            time.sleep(1.0)
            vectors = embed_texts(batch_texts)

        # For each vector in batch, upsert into DB
        for i, vec in enumerate(vectors):
            chunk_obj = chunks[index + i]
            try:
                upsert_embedding(
                    chunk_obj["chunk_id"],
                    chunk_obj["text"],
                    chunk_obj["page"],
                    chunk_obj["source"],
                    chunk_obj["metadata"],
                    vec
                )
            except Exception as e:
                print(f"[ERROR] Failed upsert for chunk {chunk_obj['chunk_id']} (page {chunk_obj['page']}): {e}")
            else:
                # create page node in Neo4j once per page (idempotent MERGE on page)
                try:
                    pg = chunk_obj["page"]
                    if pg not in pages_seen:
                        pages_seen.add(pg)
                        driver = get_driver()
                        with driver.session() as session:
                            # create a brief excerpt for the node
                            excerpt = (chunk_obj["text"][:300] + "...") if len(chunk_obj["text"]) > 300 else chunk_obj["text"]
                            session.write_transaction(create_page_node, pg, excerpt, chunk_obj.get("source", "TamilBook"))
                except Exception as e:
                    # non-fatal: log and continue
                    print(f"[WARN] Neo4j page node write error for page {chunk_obj['page']}: {e}")

        index += len(vectors)
        print(f"Processed {min(index, total)}/{total} chunks.")
        time.sleep(SLEEP_BETWEEN_BATCHES)  # polite pacing

    print("All batches processed.")


def main():
    if not os.path.exists(PDF_PATH):
        raise SystemExit(f"PDF file not found at {PDF_PATH}. Place the Tamil book PDF at this path or set PDF_PATH env var.")

    print("Starting ingestion for:", PDF_PATH)
    pages = extract_pages(PDF_PATH, ocr_language="ta")
    print(f"Extracted {len(pages)} pages (with OCR).")

    chunks = prepare_chunks_from_pages(pages)
    print(f"Prepared {len(chunks)} text chunks for embedding.")

    if not chunks:
        print("No chunks to embed. Exiting.")
        return

    upsert_chunks_with_embeddings(chunks)
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
