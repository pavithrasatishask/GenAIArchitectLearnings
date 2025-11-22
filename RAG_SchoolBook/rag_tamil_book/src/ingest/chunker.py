# ingest/chunker.py
import os
from dotenv import load_dotenv
load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 2000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 400))

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = text or ""
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + chunk_size, L)
        chunk = text[start:end]
        chunks.append({"text": chunk, "start": start, "end": end})
        start += chunk_size - overlap
    return chunks
