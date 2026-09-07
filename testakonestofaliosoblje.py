import json

courses = [json.loads(l) for l in open("data/courses.jsonl", encoding="utf-8")]
teaching = [json.loads(l) for l in open("data/teaching.jsonl", encoding="utf-8")]

course_codes = set(c.get("code") for c in courses if c.get("code"))
teaching_codes = set(t.get("code") for t in teaching if t.get("code"))

print("Kodova u courses.jsonl:", len(course_codes))
print("Kodova u teaching.jsonl:", len(teaching_codes))
print("Preklapanje:", len(course_codes & teaching_codes))
print("Samo u courses:", list(course_codes - teaching_codes)[:10])
print("Samo u teaching:", list(teaching_codes - course_codes)[:10])

# koliko kolegija ukupno i dalje nema kod
missing = [c["title"] for c in courses if not c.get("code")]
print("\nJoš uvijek bez koda:", len(missing))
print(missing[:10])

# provjerava se par nesparenih kodova rucno tj. je li stvarno razlicit kolegij ili format
only_courses_sample = [c for c in courses if c.get("code") in ["M134", "F003", "MI003"]]
for c in only_courses_sample:
    print(c["title"], "-", c["code"], "-", c["url"])

only_teaching_sample = [t for t in teaching if t.get("code") in ["M011", "M059", "M027"]]
for t in only_teaching_sample:
    print(t["nameHr"] if "nameHr" in t else t, "-", t["code"])