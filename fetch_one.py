import requests, json

r = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/pages",
                 params={"per_page": 1})

data = r.json()

print("Status:", r.status_code)
print("Ukupno stranica:", r.headers.get("X-WP-Total"))
print("Broj stranica paginacije:", r.headers.get("X-WP-TotalPages"))
print(json.dumps(data[0], indent=2, ensure_ascii=False)[:2000])