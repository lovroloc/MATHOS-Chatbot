import json

def chunk(text, size=800, overlap=100):
    parts, i = [], 0
    while i < len(text):
        parts.append(text[i:i+size])
        i += size - overlap
    return parts

out = open("data/chunks.jsonl", "w", encoding="utf-8")
n = 0
for line in open("data/docs.jsonl", encoding="utf-8"):
    doc = json.loads(line)
    for pos, part in enumerate(chunk(doc["text"])):
        out.write(json.dumps({
            "chunk_id": f"{doc['doc_id']}-{pos}",
            "doc_id": doc["doc_id"],
            "text": part,
            "title": doc["title"],
            "url": doc["url"],
            "position": pos,
        }, ensure_ascii=False) + "\n")
        n += 1
out.close()
print("Chunkova:", n)

lens = []
for line in open("data/chunks.jsonl", encoding="utf-8"):
    c = json.loads(line)
    lens.append(len(c["text"]))

lens.sort()
print("min:", lens[0], "max:", lens[-1])
print("broj chunkova < 50 znakova:", sum(1 for l in lens if l < 50))
print("prosjek:", sum(lens)/len(lens))