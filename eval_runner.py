import json, unicodedata, re
from hybrid_search import hybrid_search

def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


eval_set = [json.loads(l) for l in open("data/eval_set.jsonl", encoding="utf-8")]

results = []

for q in eval_set:
    retrieved = hybrid_search(q["question"], top_n=5)
    urls = [r[0][2] for r in retrieved]
    texts = [r[0][3] for r in retrieved]

    expected_url = q.get("expected_source")
    expected_answer = str(q.get("expected_answer", ""))
    expected_any = q.get("expected_any")

    #je li ocekivani URL među dohvacenima
    url_hit_1 = expected_url in urls[:1] if expected_url != "N/A" else None
    url_hit_3 = expected_url in urls[:3] if expected_url != "N/A" else None
    url_hit_5 = expected_url in urls if expected_url != "N/A" else None

    #pojavljuje li se ocekivani odgovor u dohvacenom tekstu
    joined = norm(" ".join(texts))
    if q["category"] == "izvan_opsega":
        answer_in_context = None  #mjeri se u eval_guardrails.py
    elif expected_any:
        answer_in_context = any(norm(e) in joined for e in expected_any)
    else:
        answer_in_context = norm(expected_answer) in joined if expected_answer else None
    results.append({
        **q,
        "url_hit_1": url_hit_1,
        "url_hit_3": url_hit_3,
        "url_hit_5": url_hit_5,
        "answer_in_context": answer_in_context,
        "top_urls": urls[:3],
    })

def rate(key, subset=None):
    rows = [r for r in results if r[key] is not None]
    if subset:
        rows = [r for r in rows if r["category"] == subset]
    if not rows:
        return "n/a"
    return f"{sum(1 for r in rows if r[key])}/{len(rows)}"

print("=== RETRIEVAL ===")
print("URL u top-1:", rate("url_hit_1"))
print("URL u top-3:", rate("url_hit_3"))
print("URL u top-5:", rate("url_hit_5"))
print("Odgovor u kontekstu:", rate("answer_in_context"))

print("\n=== PO KATEGORIJI (odgovor u kontekstu) ===")
for cat in sorted(set(r["category"] for r in results)):
    print(f"  {cat}:", rate("answer_in_context", cat))

print("\n=== PROMAŠAJI ===")
for r in results:
    if r["answer_in_context"] is False:
        print(f"\n[{r['id']}] {r['question']}")
        print(f"  očekivano: {r['expected_answer']}")
        print(f"  dohvaćeno: {r['top_urls']}")

with open("data/eval_results.jsonl", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
