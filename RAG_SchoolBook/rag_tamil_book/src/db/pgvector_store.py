# db/pgvector_store.py
"""
Neon + pgvector integration layer.
Handles:
- SSL-secured Postgres connection
- Vector table initialization
- Upsert embeddings
- Vector similarity search (L2 distance)
"""

import os
import psycopg2
from psycopg2.extras import Json
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DATABASE_URL")
EMBED_DIM = int(os.getenv("EMBED_DIM", 3072))  # 3072 for text-embedding-3-large

if not DATABASE_URL:
    raise RuntimeError("NEON_DATABASE_URL missing in .env")

# Ensure SSL for Neon
if "sslmode" not in DATABASE_URL.lower():
    DATABASE_URL += "?sslmode=require"

_conn = None


def get_conn():
    """
    Maintains a single persistent psycopg2 connection.
    Registers pgvector extension on the connection.
    """
    global _conn
    if _conn is None:
        try:
            _conn = psycopg2.connect(DATABASE_URL)
            register_vector(_conn)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Neon/Postgres: {e}")
    return _conn


def initialize_schema():
    """
    Creates:
    - pgvector extension
    - embeddings table (3072-dim vectors)
    - HNSW index for fast similarity search
    """
    conn = get_conn()
    cur = conn.cursor()

    # pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # table
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

    # HNSW index (Neon recommended)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_embeddings_embedding
        ON embeddings
        USING hnsw (embedding vector_l2_ops)
        WITH (m = 16, ef_construction = 200);
    """)

    conn.commit()


def upsert_embedding(chunk_id, content, page, source, metadata, embedding_vector):
    """
    Inserts or updates a vector chunk.
    """
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO embeddings (chunk_id, content, page, source, metadata, embedding, id)
        VALUES (%s, %s, %s, %s, %s, %s, DEFAULT)
        ON CONFLICT (chunk_id) DO UPDATE
        SET
            content = EXCLUDED.content,
            page = EXCLUDED.page,
            metadata = EXCLUDED.metadata,
            embedding = EXCLUDED.embedding;
    """

    try:
        cur.execute(sql, (
            chunk_id,
            content,
            page,
            source,
            Json(metadata),
            embedding_vector
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to upsert embedding: {e}")


def query_similar(embedding_vector, top_k=5):
    """
    ANN search using L2 vector distance.
    Returns rows sorted by relevance.
    """
    conn = get_conn()
    cur = conn.cursor()

    sql = """
        SELECT
            chunk_id,
            content,
            page,
            source,
            metadata,
            embedding <-> %s AS distance
        FROM embeddings
        ORDER BY embedding <-> %s
        LIMIT %s;
    """

    cur.execute(sql, (embedding_vector, embedding_vector, top_k))
    rows = cur.fetchall()
    return rows
