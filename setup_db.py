import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5433,
    user="mathos", password="mathos", dbname="mathosbot"
)
cur = conn.cursor()

# pgvector ekstenzija
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# tablica
cur.execute("""
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT,
    title TEXT,
    url TEXT,
    text TEXT,
    doc_type TEXT,
    embedding vector(768)
);
""")

conn.commit()

# provjera
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'chunks';")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
print("Gotovo.")