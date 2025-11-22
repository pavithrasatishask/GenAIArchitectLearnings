# db/pgvector_store.py
import os
import json
import psycopg2
from psycopg2.extras import Json
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("NEON_DATABASE_URL")
EMBED_DIM = int(os.getenv("EMBED_DIM", 1536))

if not DATABASE_URL:
    raise RuntimeError("NEON_DATABASE_URL missing in .env")

_conn = None

def get_conn():
    global _conn
    if _conn is None:
        _conn = psycopg2.connect(DATABASE_URL)
        register_vector(_conn)
    return _conn

def initialize_schema():
    conn = get_conn()
    cur = conn.cursor()
    # create extension and table if not exists
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS embeddings (
      id SERIAL PRIMARY KEY,
      chunk_id TEXT UNIQUE,
      content TEXT,
      page INT,
      source TEXT,
      metadata JSONB,
      embedding vector({EMBED_DIM})
    );
    """)
    cur.execute(f"""
    CREATE INDEX IF NOT EXISTS idx_embeddings_embedding ON embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
    """)
    conn.commit()

def upsert_embedding(chunk_id, content, page, source, metadata, vector):
    conn = get_conn()
    cur = conn.cursor()
    sql = """
    INSERT INTO embeddings (chunk_id, content, page, source, metadata, embedding)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (chunk_id) DO UPDATE
      SET content = EXCLUDED.content, page = EXCLUDED.page, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding;
    """
    cur.execute(sql, (chunk_id, content, page, source, Json(metadata), vector))
    conn.commit()

def query_similar(vector, top_k=5):
    conn = get_conn()
    cur = conn.cursor()
    sql = """
    SELECT chunk_id, content, page, source, metadata, embedding <-> %s AS distance
    FROM embeddings
    ORDER BY embedding <-> %s
    LIMIT %s;
    """
    cur.execute(sql, (vector, vector, top_k))
    rows = cur.fetchall()
    # rows: (chunk_id, content, page, source, metadata, distance)
    return rows
