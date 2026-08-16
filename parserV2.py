from bs4 import BeautifulSoup
import re

import requests
import json, time

url = "https://www.mathos.unios.hr/kolegiji/inteligentni-robotski-sustavi/"
r = requests.get(url)
print("Status:", r.status_code)
print("Duljina HTML-a:", len(r.text))




def parse_course_page(html):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("article.kolegiji") or soup.select_one("article")
    if not article:
        return None

    title = article.select_one("h1.entry-title")
    title = title.get_text(strip=True) if title else None

    result = {"title": title, "sections": {}}

    # osnovne informacije
    info_div = article.select_one(".c-profile__data")
    if info_div:
        info_text = info_div.get_text(" ", strip=True)  # ključna linija — spoji sav tekst

        m = re.search(
            r"([A-ZŠĐČĆŽ0-9]+)\s*\(\s*(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)\s*\)\s*-\s*(\d+)\s*ECTS",
            info_text
        )
        if m:
            result["code"] = m.group(1)
            result["hours"] = {"predavanja": int(m.group(2)), "vjezbe": int(m.group(3)), "seminari": int(m.group(4))}
            result["ects"] = int(m.group(5))

    # sve ostale imenovane sekcije (literatura, materijali, itd.)
    for section in article.select(".c-profile__inner"):
        heading = section.select_one("h3")
        if not heading:
            continue
        key = heading.get_text(strip=True)

        items = section.select("ul li")
        if items:
            result["sections"][key] = [li.get_text(strip=True) for li in items]
        else:
            p = section.select_one("p")
            result["sections"][key] = p.get_text(strip=True) if p else None

    return result

urls = [
    "https://www.mathos.unios.hr/kolegiji/inteligentni-robotski-sustavi/",
             "https://www.mathos.unios.hr/kolegiji/operativni-sustavi/",
             "https://www.mathos.unios.hr/kolegiji/diferencijalni-racun/"
]
for u in urls:
    r = requests.get(u)
    result = parse_course_page(r.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("---")



all_links = []
page = 1
while True:
    r = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/kolegiji",
                     params={"per_page": 100, "page": page})
    if r.status_code != 200 or not r.json():
        break
    all_links.extend(item["link"] for item in r.json())
    page += 1

print("Ukupno kolegija:", len(all_links))

courses = []
for i, url in enumerate(all_links, 1):
    try:
        r = requests.get(url, timeout=30)
        parsed = parse_course_page(r.text)
        if parsed:
            parsed["url"] = url
            courses.append(parsed)
    except requests.RequestException as e:
        print(f"Greška na {url}: {e}")
    if i % 20 == 0:
        print(f"{i}/{len(all_links)}")
    time.sleep(0.3)

with open("data/courses.jsonl", "w", encoding="utf-8") as f:
    for c in courses:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print("Gotovo:", len(courses))