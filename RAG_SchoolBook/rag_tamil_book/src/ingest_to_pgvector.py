# ingest_to_pgvector.py (place in project root)
import os
from ingest.pdf_ingest import extract_pages, normalize_text
from ingest.chunker import chunk_text
from ingest.embedder import embed_texts
from db.pgvector_store import initialize_schema, upsert_embedding
from kg.neo4j_client import get_driver, create_page_node, link_topic_page
import hashlib
import json

PDF_PATH = "data/tamil_grade8_book.pdf"  # put book here

def chunk_id_for(page, idx):
    return hashlib.sha1(f"{page}-{idx}".encode("utf-8")).hexdigest()

def main():
    initialize_schema()
    pages = extract_pages(PDF_PATH, ocr_language="ta")
    all_chunks = []
    for p in pages:
        page_num = p["page"]
        text = p.get("text","")
        # include image OCR text into page text as additional provenance if present
        for im in p.get("images", []):
            if isinstance(im, dict) and im.get("ocr"):
                text += "\n" + im["ocr"].get("text", "")
        text = normalize_text(text)
        chunks = chunk_text(text)
        # attach page metadata
        for i, ch in enumerate(chunks):
            chunk_id = chunk_id_for(page_num, i)
            all_chunks.append({"chunk_id": chunk_id, "text": ch["text"], "page": page_num, "source": "TamilBook", "metadata": {"page": page_num}})
    # embed in batches
    texts = [c["text"] for c in all_chunks]
    vectors = embed_texts(texts)
    for c, vec in zip(all_chunks, vectors):
        upsert_embedding(c["chunk_id"], c["text"], c["page"], c["source"], c["metadata"], vec)
        # optionally create KG Page nodes & simple links
        try:
            driver = get_driver()
            with driver.session() as session:
                session.write_transaction(create_page_node, c["page"], c["text"][:300], "TamilBook")
                # You could detect topics and link them:
                # session.write_transaction(link_topic_page, detected_topic, c["page"])
        except Exception as e:
            print("KG write error:", e)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
