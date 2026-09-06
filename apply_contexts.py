import json, os

contexts = {}
if os.path.exists("data/contexts.jsonl"):
    for l in open("data/contexts.jsonl", encoding="utf-8"):
        d = json.loads(l)
        contexts[d["chunk_id"]] = d["context"]

print(f"Učitano konteksta: {len(contexts)}")

out = open("data/chunks_ctx.jsonl", "w", encoding="utf-8")
n_with, n_without = 0, 0

for line in open("data/chunks.jsonl", encoding="utf-8"):
    c = json.loads(line)
    ctx = contexts.get(c["chunk_id"])
    if ctx:
        c["context_prefix"] = ctx
        c["raw_text"] = c["text"]
        c["text"] = f"{ctx}\n{c['text']}"
        n_with += 1
    else:
        c["context_prefix"] = ""
        c["raw_text"] = c["text"]
        n_without += 1
    out.write(json.dumps(c, ensure_ascii=False) + "\n")

out.close()
print(f"S kontekstom: {n_with}, bez: {n_without}")