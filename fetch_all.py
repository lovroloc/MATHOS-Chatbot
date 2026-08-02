import requests, json, time, pathlib

BASE = "https://www.mathos.unios.hr/wp-json/wp/v2"
OUT = pathlib.Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

def fetch_type(kind):
    items, page = [], 1
    while True:
        r = requests.get(f"{BASE}/{kind}", params={"per_page": 100, "page": page}, timeout=30)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        items.extend(batch)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        print(f"{kind}: stranica {page}/{total_pages}, ukupno {len(items)}")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.5)  # da faks server ne blokira
    (OUT / f"{kind}.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return items


for kind in ["pages", "posts"]:
    fetch_type(kind)