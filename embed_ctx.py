import json, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")
chunks = [json.loads(l) for l in open("data/chunks_ctx.jsonl", encoding="utf-8")]
texts = ["passage: " + c["text"] for c in chunks]

emb = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
np.save("data/embeddings_ctx.npy", emb)
print(emb.shape)