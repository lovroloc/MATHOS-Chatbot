import json, numpy as np, psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(host="localhost", port=5433,
                        user="mathos", password="mathos", dbname="mathosbot")
cur = conn.cursor()

chunks = [json.loads(l) for l in open("data/chunks.jsonl", encoding="utf-8")]
emb = np.load("data/embeddings.npy")

assert len(chunks) == emb.shape[0], f"Nesklad: {len(chunks)} chunkova vs {emb.shape[0]} embeddinga"

seen = set()
rows = []
for c, v in zip(chunks, emb):
    if c["chunk_id"] in seen:
        continue
    seen.add(c["chunk_id"])
    rows.append((c["chunk_id"], c["doc_id"], c.get("title"), c.get("url"),
                 c["text"], c.get("doc_type"), v.tolist()))

print(f"Preskočeno duplikata: {len(chunks) - len(rows)}")

execute_values(cur, """
    INSERT INTO chunks (chunk_id, doc_id, title, url, text, doc_type, embedding)
    VALUES %s
    ON CONFLICT (chunk_id) DO UPDATE SET
        text = EXCLUDED.text,
        embedding = EXCLUDED.embedding
""", rows, template="(%s, %s, %s, %s, %s, %s, %s::vector)")

conn.commit()
print("Ubačeno:", len(rows))