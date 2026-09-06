import psycopg2, re
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", max_length=512)
    return _reranker

model = SentenceTransformer("intfloat/multilingual-e5-base")
conn = psycopg2.connect(host="localhost", port=5433,
                        user="mathos", password="mathos", dbname="mathosbot")

STOP_HR = {"kad", "je", "su", "koji", "koja", "koje", "kako", "gdje", "sto", "što",
           "za", "na", "od", "do", "u", "i", "a", "li", "se", "mi", "mogu",
           "nosi", "ima", "biti", "bi", "the", "of"}

def vector_search(query, k=20, table="chunks_ctx"):
    qv = model.encode(["query: " + query], normalize_embeddings=True)[0].tolist()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT chunk_id, title, url, text, 1 - (embedding <=> %s::vector) AS score
        FROM {table}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (qv, qv, k))
    return cur.fetchall()


def lexical_search(query, k=20, table="chunks_ctx"):
    tokens = re.findall(r"\w+", query.lower(), flags=re.UNICODE)
    tokens = [t for t in tokens if len(t) > 2 and t not in STOP_HR]
    if not tokens:
        return []
    tsquery = " | ".join(tokens)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT chunk_id, title, url, text,
               ts_rank(tsv, to_tsquery('simple', %s)) AS score
        FROM {table}
        WHERE tsv @@ to_tsquery('simple', %s)
        ORDER BY score DESC
        LIMIT %s
    """, (tsquery, tsquery, k))
    return cur.fetchall()

def rrf_fuse(result_lists, weights=None, k=60, top_n=5):
    scores, meta, raw = {}, {}, {}
    if weights is None:
        weights = [1.0] * len(result_lists)
    for li, (results, w) in enumerate(zip(result_lists, weights)):
        for rank, row in enumerate(results, 1):
            cid = row[0]
            scores[cid] = scores.get(cid, 0) + w / (k + rank)
            meta[cid] = row
            if li == 0:                      # vektorska lista
                raw[cid] = row[4]
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
    return [(meta[cid], s, raw.get(cid, 0.0)) for cid, s in ranked]

def hybrid_search(query, top_n=5, mode="hybrid", k_candidates=20,
                  bm25_weight=1.0, rerank=False, rerank_pool=20, table="chunks_ctx"):
    lists, weights = [], []
    if mode in ("hybrid", "vector"):
        lists.append(vector_search(query, k=k_candidates, table=table))
        weights.append(1.0)
    if mode in ("hybrid", "bm25"):
        lists.append(lexical_search(query, k=k_candidates, table=table))
        weights.append(bm25_weight)
    if not lists:
        return []

    fused = rrf_fuse(lists, weights=weights, top_n=rerank_pool if rerank else top_n)

    if not rerank or not fused:
        return fused

    model = get_reranker()
    pairs = [(query, item[0][3]) for item in fused]
    scores = model.predict(pairs)

    ranked = sorted(zip(fused, scores), key=lambda x: -x[1])[:top_n]
    return [(item[0], item[1], float(s)) for item, s in ranked]

if __name__ == "__main__":
    while True:
        q = input("\nPitanje (prazno za izlaz): ").strip()
        if not q:
            break
        for (cid, title, url, text, _), score in hybrid_search(q):
            print(f"\n[{score:.4f}] {title}")
            print(f"  {url}")
            print(f"  {text[:250]}...")