import json, time, unicodedata, re
from generate import answer

def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()

eval_set = [json.loads(l) for l in open("data/eval_set.jsonl", encoding="utf-8")]
qs = [q for q in eval_set if q.get("category") != "izvan_opsega"]

results = []
for i, q in enumerate(qs, 1):
    text, sources = answer(q["question"])
    n = norm(text)

    expected_any = q.get("expected_any")
    if expected_any:
        ok = any(norm(e) in n for e in expected_any)
    else:
        ok = norm(q.get("expected_answer", "")) in n

    results.append({**q, "answer": text, "correct": ok})
    print(f"[{'OK ' if ok else 'FAIL'}] {q['id']} {q['question']}")
    if not ok:
        print(f"       očekivano: {q.get('expected_any') or q.get('expected_answer')}")
        print(f"       dobiveno:  {text[:150]}")

    time.sleep(1) # da se ne predje rate limit

print(f"\n=== TOČNIH ODGOVORA: {sum(1 for r in results if r['correct'])}/{len(results)} ===")

by_cat = {}
for r in results:
    c = r["category"]
    by_cat.setdefault(c, [0, 0])
    by_cat[c][1] += 1
    if r["correct"]:
        by_cat[c][0] += 1

print("\n=== PO KATEGORIJI ===")
for c, (ok, total) in sorted(by_cat.items()):
    print(f"  {c}: {ok}/{total}")

with open("data/eval_generation_results.jsonl", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")