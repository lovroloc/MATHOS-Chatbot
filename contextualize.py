import json, os, time, random
from collections import defaultdict
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SAMPLE_SIZE = 350
SLEEP = 4.2 # 15 zahtjeva/min limit

PROMPT = """Evo cijelog dokumenta:
<dokument>
{doc}
</dokument>

Evo odsječka iz tog dokumenta:
<odsjecak>
{chunk}
</odsjecak>

Napiši 1-2 kratke rečenice na hrvatskom koje smještaju ovaj odsječak u kontekst cijelog dokumenta, kako bi se lakše pronašao pretragom. Odgovori SAMO tim rečenicama, bez uvoda."""

docs = {}
for l in open("data/docs_all.jsonl", encoding="utf-8"):
    d = json.loads(l)
    docs[d["doc_id"]] = d

chunks = [json.loads(l) for l in open("data/chunks.jsonl", encoding="utf-8")]

counts = defaultdict(int)
for c in chunks:
    counts[c["doc_id"]] += 1

multi = [c for c in chunks if counts[c["doc_id"]] > 1]

# deterministicki uzorak da je ponovljiv
random.seed(42)
sample = random.sample(multi, min(SAMPLE_SIZE, len(multi)))

print(f"Ukupno chunkova: {len(chunks)}")
print(f"Višechunkovnih: {len(multi)}")
print(f"Uzorak za kontekstualizaciju: {len(sample)}")

done = {}
if os.path.exists("data/contexts.jsonl"):
    for l in open("data/contexts.jsonl", encoding="utf-8"):
        d = json.loads(l)
        done[d["chunk_id"]] = d["context"]
    print(f"Već obrađeno: {len(done)}")

todo = [c for c in sample if c["chunk_id"] not in done]
print(f"Preostalo: {len(todo)}")
print(f"Procjena trajanja: {len(todo) * SLEEP / 60:.0f} min\n")

out = open("data/contexts.jsonl", "a", encoding="utf-8")

for i, c in enumerate(todo, 1):
    doc_text = docs[c["doc_id"]]["text"][:6000]
    ctx = None

    for attempt in range(3):
        try:
            r = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(max_output_tokens=120, temperature=0.0),
                contents=PROMPT.format(doc=doc_text, chunk=c["text"]),
            )
            ctx = r.text.strip()
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                print(f"  rate limit, čekam 30s...")
                time.sleep(30)
                continue
            print(f"  greška na {c['chunk_id']}: {str(e)[:100]}")
            break

    if ctx:
        out.write(json.dumps({"chunk_id": c["chunk_id"], "context": ctx},
                             ensure_ascii=False) + "\n")
        out.flush()

    if i % 20 == 0:
        print(f"  {i}/{len(todo)}")
    time.sleep(SLEEP)

out.close()
print("\nGotovo.")