import json, pathlib
from bs4 import BeautifulSoup
import re

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)      # višak praznih redaka
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


out = open("data/docs.jsonl", "w", encoding="utf-8")


for kind in ["pages", "posts"]:
    items = json.loads(pathlib.Path(f"data/raw/{kind}.json").read_text(encoding="utf-8"))
    for it in items:
        text = html_to_text(it["content"]["rendered"])
        if len(text) < 100:          # preskoči prazne stranice
            continue
        doc = {
            "doc_id": f"{kind}-{it['id']}",
            "title": BeautifulSoup(it["title"]["rendered"], "html.parser").get_text(),
            "url": it["link"],
            "text": text,
            "modified": it["modified"],
            "doc_type": kind,
        }
        out.write(json.dumps(doc, ensure_ascii=False) + "\n")

out.close()