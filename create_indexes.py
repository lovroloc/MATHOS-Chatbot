import psycopg2

conn = psycopg2.connect(host="localhost", port=5433,
                        user="mathos", password="mathos", dbname="mathosbot")
cur = conn.cursor()

cur.execute("""
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks USING hnsw (embedding vector_cosine_ops);
""")

# leksicki -> generirani tsvector stupac
cur.execute("""
ALTER TABLE chunks
ADD COLUMN IF NOT EXISTS tsv tsvector
GENERATED ALWAYS AS (to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(text,''))) STORED;
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv);
""")

conn.commit()
print("Indeksi spremni.")