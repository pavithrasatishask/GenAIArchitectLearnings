-- schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
  id SERIAL PRIMARY KEY,
  chunk_id TEXT UNIQUE,
  content TEXT,
  page INT,
  source TEXT,
  metadata JSONB,
  embedding vector(1536)
);

-- ivfflat index for approximate nearest neighbor search
-- Tune lists depending on dataset size (100 is an initial suggestion)
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding ON embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
