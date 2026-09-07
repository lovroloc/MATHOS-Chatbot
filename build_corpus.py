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

    staff_urls = json.load(open("data/staff_urls.json", encoding="utf-8"))
    docs.append({
        "doc_id": f"staff-{s['id']}",
        "title": f"{s['firstName']} {s['lastName']}",
        "url": staff_urls.get(str(s["id"])),
        "text": " ".join(parts),
        "doc_type": "staff",
    })

# kolegiji = tekst iz scrapinga + tko predaje (spojeno iz teaching.jsonl)
teaching = [json.loads(l) for l in open("data/teaching.jsonl", encoding="utf-8")]
courses = [json.loads(l) for l in open("data/courses.jsonl", encoding="utf-8")]

teaching_by_code = {}
for t in teaching:
    teaching_by_code.setdefault(t["code"], []).append(t)

ROLE_HR = {
    "lead": "nositelj",
    "assistant": "asistent",
    "lecturer": "predavač",
}

for c in courses:
    parts = [f"Kolegij: {c['title']}."]
    if c.get("code"):
        parts.append(f"Šifra kolegija: {c['code']}.")
    if c.get("ects"):
        parts.append(f"Nosi {c['ects']} ECTS bodova.")
    if c.get("hours"):
        h = c["hours"]
        parts.append(f"Tjedno: {h['predavanja']} sati predavanja, {h['vjezbe']} vježbi, {h['seminari']} seminara.")
    if c.get("description"):
        parts.append(c["description"])
    if c.get("code") and c["code"] in teaching_by_code:
        names = sorted(set(
            f"{t['firstName']} {t['lastName']} ({ROLE_HR.get(t['role'], t['role'])})"
            for t in teaching_by_code[c["code"]]
        ))
        parts.append("Nositelji i izvođači: " + ", ".join(names) + ".")
    lit = c.get("sections", {}).get("Osnovna literatura")
    if lit:
        parts.append("Osnovna literatura: " + "; ".join(lit) + ".")

    docs.append({
        "doc_id": f"course-{c['url'].rstrip('/').split('/')[-1]}",
        "title": c["title"],
        "url": c["url"],
        "text": " ".join(parts),
        "doc_type": "course",
    })

docs.append({
    "doc_id": "info-materijali",
    "title": "Materijali za kolegije",
    "url": "https://www.mathos.unios.hr/kolegiji/",
    "text": "Materijali za kolegije dostupni su na internom Teams kanalu svakog kolegija. "
            "Studenti su obvezni registrirati se na Teams kanal kolegija. "
            "Šifra kanala nalazi se u rasporedu.",
    "doc_type": "info",
})

with open("data/docs_combined.jsonl", "w", encoding="utf-8") as f:
    for d in docs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print("Ukupno kombiniranih dokumenata:", len(docs))
