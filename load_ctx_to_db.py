import json, numpy as np, psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(host="localhost", port=5433,
                        user="mathos", password="mathos", dbname="mathosbot")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS chunks_ctx (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT, title TEXT, url TEXT,
    text TEXT, doc_type TEXT,
    embedding vector(768)
);
""")
conn.commit()

chunks = [json.loads(l) for l in open("data/chunks_ctx.jsonl", encoding="utf-8")]
emb = np.load("data/embeddings_ctx.npy")
assert len(chunks) == emb.shape[0]

seen, rows = set(), []
for c, v in zip(chunks, emb):
    if c["chunk_id"] in seen:
        continue
    seen.add(c["chunk_id"])
    rows.append((c["chunk_id"], c["doc_id"], c.get("title"), c.get("url"),
                 c["text"], c.get("doc_type"), v.tolist()))

execute_values(cur, """
    INSERT INTO chunks_ctx (chunk_id, doc_id, title, url, text, doc_type, embedding)
    VALUES %s ON CONFLICT (chunk_id) DO UPDATE SET
        text = EXCLUDED.text, embedding = EXCLUDED.embedding
""", rows, template="(%s, %s, %s, %s, %s, %s, %s::vector)")

cur.execute("CREATE INDEX IF NOT EXISTS chunks_ctx_emb_idx ON chunks_ctx USING hnsw (embedding vector_cosine_ops);")
cur.execute("""
ALTER TABLE chunks_ctx ADD COLUMN IF NOT EXISTS tsv tsvector
GENERATED ALWAYS AS (to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(text,''))) STORED;
""")
cur.execute("CREATE INDEX IF NOT EXISTS chunks_ctx_tsv_idx ON chunks_ctx USING GIN (tsv);")
conn.commit()
print("Ubačeno:", len(rows))