import json, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")
chunks = [json.loads(l) for l in open("data/chunks.jsonl", encoding="utf-8")]
emb = np.load("data/embeddings.npy")

while True:
    q = input("\nPitanje (prazno za izlaz): ").strip()
    if not q:
        break
    qv = model.encode(["query: " + q], normalize_embeddings=True)[0]
    scores = emb @ qv
    top = np.argsort(-scores)[:3]
    for rank, i in enumerate(top, 1):
        c = chunks[i]
        print(f"\n[{rank}] {scores[i]:.3f}  {c['title']}")
        print(f"    {c['url']}")
        print(f"    {c['text'][:300]}...")