import json

out = open("data/docs_all.jsonl", "w", encoding="utf-8")
n = 0

# WP stranice, objave, obavijesti
for line in open("data/docs.jsonl", encoding="utf-8"):
    d = json.loads(line)
    d.setdefault("doc_type", "wp")
    out.write(json.dumps(d, ensure_ascii=False) + "\n")
    n += 1

# osoblje + kolegiji iz build_corpus.py
for line in open("data/docs_combined.jsonl", encoding="utf-8"):
    out.write(line)
    n += 1

out.close()
print("Ukupno dokumenata:", n)