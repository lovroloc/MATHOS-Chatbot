import json

def chunk(text, target=600):
    #reze po odlomcima, spaja male, ne sijece usred recenice
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, current = [], ""

    for p in paragraphs:
        if len(current) + len(p) + 1 <= target:
            current = (current + "\n" + p).strip()
        else:
            if current:
                chunks.append(current)
            if len(p) > target * 1.5:
                sentences = p.split(". ")
                buf = ""
                for s in sentences:
                    if len(buf) + len(s) + 2 <= target:
                        buf = (buf + ". " + s).strip(". ")
                    else:
                        if buf:
                            chunks.append(buf)
                        buf = s
                if buf:
                    chunks.append(buf)
                current = ""
            else:
                current = p

    if current:
        chunks.append(current)
    return chunks


out = open("data/chunks.jsonl", "w", encoding="utf-8")
n = 0
for line in open("data/docs_all.jsonl", encoding="utf-8"):
    doc = json.loads(line)
    for pos, part in enumerate(chunk(doc["text"])):
        if len(part) < 50: #preskoci degenerirane
            continue
        prefixed = f"{doc['title']}\n{part}" if doc.get("title") else part
        out.write(json.dumps({
            "chunk_id": f"{doc['doc_id']}-{pos}",
            "doc_id": doc["doc_id"],
            "text": prefixed,
            "title": doc["title"],
            "url": doc["url"],
            "doc_type": doc.get("doc_type"),
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