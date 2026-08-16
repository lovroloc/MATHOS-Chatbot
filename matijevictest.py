import json, random
courses = [json.loads(l) for l in open("data/courses.jsonl", encoding="utf-8")]
sample = random.sample([c for c in courses if c.get("ects")], 10)
for c in sample:
    print(c["title"], "-", c["ects"], "ECTS -", c["url"])