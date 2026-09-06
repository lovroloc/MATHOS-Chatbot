import psycopg2

conn = psycopg2.connect(host="localhost", port=5433,   # provjeri je li 5432 ili 5433 kod tebe
                        user="mathos", password="mathos", dbname="mathosbot")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM chunks")
print("Ukupno chunkova u bazi:", cur.fetchone()[0])

cur.execute("SELECT doc_type, COUNT(*) FROM chunks GROUP BY doc_type ORDER BY 2 DESC")
print("\nPo tipu dokumenta:")
for row in cur.fetchall():
    print(" ", row)

cur.execute("SELECT COUNT(*) FROM chunks WHERE url LIKE '%%/kolegiji/%%'")
print("\nChunkova s /kolegiji/ URL-om:", cur.fetchone()[0])

cur.execute("SELECT title, url FROM chunks WHERE url LIKE '%%/kolegiji/%%' LIMIT 5")
print("\nPrimjeri:")
for row in cur.fetchall():
    print(" ", row)

cur.close()
conn.close()