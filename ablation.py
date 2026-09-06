import json, unicodedata, re
from hybrid_search import hybrid_search

def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()

eval_set = [json.loads(l) for l in open("data/eval_set.jsonl", encoding="utf-8")]
qs = [q for q in eval_set if q.get("category") != "izvan_opsega"]


def run(mode, top_n, bm25_weight=1.0, rerank=False, rerank_pool=20, table="chunks"):
    hits, url_hits, url_total = 0, 0, 0
    by_cat = {}
    for q in qs:
        res = hybrid_search(q["question"], top_n=top_n, mode=mode,
                            bm25_weight=bm25_weight, rerank=rerank,
                            rerank_pool=rerank_pool, table=table)
        texts = norm(" ".join(r[0][3] for r in res))
        urls = [r[0][2] for r in res]

        exp_any = q.get("expected_any")
        if exp_any:
            ok = any(norm(e) in texts for e in exp_any)
        else:
            ok = norm(q.get("expected_answer", "")) in texts
        hits += ok

        cat = q["category"]
        by_cat.setdefault(cat, [0, 0])
        by_cat[cat][1] += 1
        by_cat[cat][0] += ok

        exp_url = q.get("expected_source")
        if exp_url and exp_url != "N/A":
            url_total += 1
            url_hits += exp_url in urls
    return hits, url_hits, url_total, by_cat

print(f"{'Konfiguracija':<28} {'Odgovor':>10} {'URL':>10}")
print("-" * 50)

configs = [
    ("Bez konteksta",       "hybrid", 5, 1.0, False, 20, "chunks"),
    ("S kontekstom (332)",  "hybrid", 5, 1.0, False, 20, "chunks_ctx"),
]

rows = []
for label, mode, k, w, rr, pool, tbl in configs:
    h, uh, ut, by_cat = run(mode, k, w, rr, pool, tbl)
    sifra = by_cat.get("sifra", [0, 0])
    print(f"{label:<24} {h:>5}/{len(qs):<4} {uh:>5}/{ut:<4}  šifre: {sifra[0]}/{sifra[1]}")
    rows.append({"config": label, "table": tbl, "answer_hits": h,
                 "answer_total": len(qs), "url_hits": uh, "url_total": ut,
                 "by_category": by_cat})

with open("data/ablation_results.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)