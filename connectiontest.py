import mysql.connector
import requests

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="chatbot",
    password="eZi#i0o9i",
    database="intranet"
)
print("Spojeno:", conn.is_connected())

r = requests.get("https://www.mathos.unios.hr/wp-json/wp/v2/kolegiji", params={"per_page": 1})
data = r.json()[0]
print(data["title"]["rendered"])
print(data["content"]["rendered"][:1000])
print(data["link"])
print(repr(data["content"]["rendered"]))
print("Duljina:", len(data["content"]["rendered"]))
