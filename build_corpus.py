import json

docs = []

# osoblje → tekstualni opis
staff = [json.loads(l) for l in open("data/staff.jsonl", encoding="utf-8")]
for s in staff:
    parts = [f"{s.get('title', '')} {s['firstName']} {s['lastName']}".strip()]
    if s.get("chair"):
        parts.append(f"Član je {s['chair']}.")
    if s.get("types"):
        parts.append(f"Uloga: {s['types']}.")
    if s.get("email"):
        parts.append(f"E-mail: {s['email']}.")
    if s.get("room"):
        parts.append(f"Soba: {s['room']}.")
    if s.get("phoneNumber"):
        parts.append(f"Telefon: {s['phoneNumber']}.")

    docs.append({
        "doc_id": f"staff-{s['id']}",
        "title": f"{s['firstName']} {s['lastName']}",
        "url": None,  # nema pojedinačnog URL-a osim ako dodamo moj_profil link
        "text": " ".join(parts),
        "doc_type": "staff",
    })

# kolegiji → tekst iz scrapinga + tko predaje (spojeno iz teaching.jsonl)
teaching = [json.loads(l) for l in open("data/teaching.jsonl", encoding="utf-8")]
courses = [json.loads(l) for l in open("data/courses.jsonl", encoding="utf-8")]

teaching_by_code = {}
for t in teaching:
    teaching_by_code.setdefault(t["code"], []).append(t)

for c in courses:
    parts = [c.get("description", "")]
    if c.get("code") and c["code"] in teaching_by_code:
        names = sorted(set(f"{t['firstName']} {t['lastName']} ({t['role']})" for t in teaching_by_code[c["code"]]))
        parts.append("Nositelji/izvođači: " + ", ".join(names) + ".")
    if c.get("ects"):
        parts.append(f"Nosi {c['ects']} ECTS bodova.")
    lit = c.get("sections", {}).get("Osnovna literatura")
    if lit:
        parts.append("Osnovna literatura: " + "; ".join(lit) + ".")

    docs.append({
        "doc_id": f"course-{c.get('code', c['title'])}",
        "title": c["title"],
        "url": c["url"],
        "text": " ".join(p for p in parts if p),
        "doc_type": "course",
    })

with open("data/docs_combined.jsonl", "w", encoding="utf-8") as f:
    for d in docs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print("Ukupno kombiniranih dokumenata:", len(docs))