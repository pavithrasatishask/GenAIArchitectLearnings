# embed/embedder.py
import os
from openai import OpenAI
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_texts(texts, model="text-embedding-3-small"):
    resp = openai.embeddings.create(model=model, input=texts)
    vectors = [item["embedding"] for item in resp["data"]]
    return vectors
