-- schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
  id SERIAL PRIMARY KEY,
  chunk_id TEXT UNIQUE,
  content TEXT,
  page INT,
  source TEXT,
  metadata JSONB,
  embedding vector(3072)
);

-- Example HNSW index for fast ANN (preferred for Neon)
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding
ON embeddings
USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 200);