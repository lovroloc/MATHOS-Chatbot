import json, random

courses = [json.loads(l) for l in open("data/courses.jsonl", encoding="utf-8")]
staff = [json.loads(l) for l in open("data/staff.jsonl", encoding="utf-8")]

questions = []
qid = 1

# 10 pitanja o ECTS-u kolegija
for c in random.sample([c for c in courses if c.get("ects")], 10):
    questions.append({
        "id": f"q{qid:03d}",
        "question": f"Koliko ECTS bodova nosi {c['title']}?",
        "expected_answer": f"{c['ects']} ECTS",
        "expected_source": c["url"],
        "category": "kolegiji",
        "difficulty": "easy",
    })
    qid += 1

# 10 pitanja o mailovima osoblja
for s in random.sample([s for s in staff if s.get("email")], 10):
    questions.append({
        "id": f"q{qid:03d}",
        "question": f"Koji je e-mail od {s['firstName']} {s['lastName']}?",
        "expected_answer": s["email"],
        "expected_source": "N/A",
        "category": "osoblje",
        "difficulty": "easy",
    })
    qid += 1

with open("data/eval_set.jsonl", "w", encoding="utf-8") as f:
    for q in questions:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")

print("Generirano pitanja:", len(questions))
print("Sad ručno dopiši ostalih 20 u data/eval_set.jsonl")