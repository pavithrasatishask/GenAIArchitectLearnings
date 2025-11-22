# ingest/embedder.py
import os
import time
import unicodedata
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import backoff

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")

client = OpenAI(api_key=OPENAI_API_KEY)

def normalize(text: str) -> str:
    """Unicode normalization + strip."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text).strip()


@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def embed_batch(batch: List[str]):
    """
    Embeds a batch of strings using OpenAI newer embedding API.
    """
    response = client.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=batch
    )
    # response.data is a list of embeddings in order
    return [item.embedding for item in response.data]


def embed_texts(texts: List[str], batch_size=16, sleep_between=0.05):
    """
    Batch embed text list and return vector list
    """
    cleaned = [normalize(t) for t in texts]

    vectors = []
    for i in range(0, len(cleaned), batch_size):
        batch = cleaned[i:i + batch_size]
        batch_vectors = embed_batch(batch)
        vectors.extend(batch_vectors)
        time.sleep(sleep_between)

    return vectors
