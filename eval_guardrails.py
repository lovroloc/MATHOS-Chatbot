import json
from generate import answer

eval_set = [json.loads(l) for l in open("data/eval_set.jsonl", encoding="utf-8")]
guardrail_qs = [q for q in eval_set if q.get("category") == "izvan_opsega"]

REFUSAL_MARKERS = ["nemam informaciju", "studomat", "obratite se referadi", "ne mogu"]

results = []
for q in guardrail_qs:
    text, sources = answer(q["question"])
    refused = any(m in text.lower() for m in REFUSAL_MARKERS)
    results.append({**q, "answer": text, "refused": refused})
    print(f"[{'OK ' if refused else 'FAIL'}] {q['question']}")
    print(f"       {text[:150]}\n")

passed = sum(1 for r in results if r["refused"])
print(f"=== ODBIJANJE: {passed}/{len(results)} ===")

with open("data/eval_guardrails_results.jsonl", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")