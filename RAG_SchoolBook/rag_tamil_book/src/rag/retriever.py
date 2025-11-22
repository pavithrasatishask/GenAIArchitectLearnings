# rag/retriever.py
from ingest.embedder import embed_texts
from db.pgvector_store import query_similar

def retrieve(question, top_k=5):
    q_vec = embed_texts([question])[0]
    rows = query_similar(q_vec, top_k=top_k)
    # rows: (chunk_id, content, page, source, metadata, distance)
    results = []
    for r in rows:
        chunk_id, content, page, source, metadata, distance = r
        results.append({"chunk_id": chunk_id, "content": content, "page": page, "source": source, "metadata": metadata, "distance": distance})
    return results
