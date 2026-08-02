import json, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")

chunks = [json.loads(l) for l in open("data/chunks.jsonl", encoding="utf-8")]
texts = ["passage: " + c["text"] for c in chunks]   # e5 traži ovaj prefiks

emb = model.encode(texts, batch_size=32, show_progress_bar=True,
                   normalize_embeddings=True)

np.save("data/embeddings.npy", emb)
print(emb.shape)