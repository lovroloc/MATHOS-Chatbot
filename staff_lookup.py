import json, re, unicodedata
from difflib import SequenceMatcher

staff = [json.loads(l) for l in open("data/staff.jsonl", encoding="utf-8")]

def normalize(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z ]", "", s)

# predizračunaj normalizirana imena
for s in staff:
    s["_norm"] = normalize(f"{s['firstName']} {s['lastName']}")

STOPWORDS = {"profesor", "profesora", "profesorica", "docent", "asistent",
             "kolegij", "kolegija", "kolegiju", "predmet", "predmeta",
             "koliko", "bodova", "nosi", "kontakt", "trebam", "mail",
             "email", "telefon", "soba", "sobi", "katedra", "katedri",
             "algebra", "analiza", "matematika", "informatika", "statistika"}

def find_person(query, threshold=0.85):
    """Vrati najbolji pogodak po imenu iz upita, ili None."""
    q = normalize(query)
    candidates = []
    for s in staff:
        last = normalize(s["lastName"])
        first = normalize(s["firstName"])

        last_score, first_score = 0, 0
        for token in q.split():
            if token in STOPWORDS:
                continue
            if len(token) < 5:
                if token == last:
                    last_score = max(last_score, 1.0)
                elif token == first:
                    first_score = max(first_score, 1.0)
                continue
            last_score = max(last_score, SequenceMatcher(None, token, last).ratio())
            first_score = max(first_score, SequenceMatcher(None, token, first).ratio())

        if last_score >= 0.85:
            candidates.append((s, last_score, first_score))

    if not candidates:
        return None, 0

    # ako više osoba dijeli prezime, ime mora presuditi
    if len(candidates) > 1:
        candidates.sort(key=lambda x: -x[2])
        if candidates[0][2] < 0.85:
            return None, candidates[0][1]   # dvosmisleno → pusti na RAG
        return candidates[0][0], 1.0

    return candidates[0][0], candidates[0][1]

def format_person(s):
    parts = [f"{s.get('title') or ''} {s['firstName']} {s['lastName']}".strip()]
    if s.get("chair"):
        parts.append(f"Katedra: {s['chair']}.")
    if s.get("types"):
        parts.append(f"Uloga: {s['types']}.")
    if s.get("email"):
        parts.append(f"E-mail: {s['email']}.")
    if s.get("room"):
        parts.append(f"Soba: {s['room']}.")
    if s.get("phoneNumber"):
        parts.append(f"Telefon: {s['phoneNumber']}.")
    return " ".join(parts)

if __name__ == "__main__":
    for q in ["trebam mail od profesora Matijevica",
              "kontakt Kristian Sabo",
              "u kojoj sobi je Mirta Bensic",
              "koliko ECTS-a nosi algebra"]:
        person, score = find_person(q)
        print(f"\n{q}\n  score={score:.2f}  →  {format_person(person) if person else 'NEMA'}")