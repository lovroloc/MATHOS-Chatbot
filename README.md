# Mathos RAG chatbot

Chatbot za web stranicu Fakulteta primijenjene matematike i informatike u Osijeku.

## Arhitektura

Izvori podataka:
- WordPress REST API (`pages`, `posts`, `aktualne_obavijesti`)
- HTML scraping renderiranih stranica (`kolegiji`)
- MySQL intranet baza preko SSH tunela (osoblje, nastava)

Pipeline: dohvat → čišćenje → semantički chunking → contextual retrieval →
embeddinzi (multilingual-e5-base) → pgvector + GIN indeks →
hibridni dohvat (vektorski + BM25, RRF fuzija) → Gemini generacija

## Pokretanje

### Preduvjeti
- Docker Desktop
- Python 3.11+
- Gemini API ključ u `.env` kao `GOOGLE_API_KEY`

### Baza
```bash
docker compose up -d
python setup_db.py
```

### Punjenje podataka
```bash
python fetch_all.py           # WP REST API
python clean.py               # čišćenje HTML-a
python parserV2.py            # scraping kolegija
python fetch_staff_from_db.py # osoblje iz MySQL-a (traži SSH tunel)
python fetch_teaching_from_db.py
python build_corpus.py        # spajanje izvora
python chunk_generation.py
python embed.py
python load_to_db.py
python create_indexes.py
```

### Contextual Retrieval (opcionalno)
```bash
python contextualize.py       # generira kontekste (troši API kvotu)
python apply_contexts.py
python embed_ctx.py
python load_ctx_to_db.py
```

### Pokretanje servisa
```bash
uvicorn api:app --port 8000
cd widget && python -m http.server 3000
```

## Evaluacija
```bash
python eval_runner.py         # retrieval, ne troši API
python eval_generation.py     # točnost odgovora
python eval_guardrails.py     # odbijanje upita izvan opsega
python ablation.py            # ablacijske studije
python latency_test.py
```

Rezultati u `data/eval_history.md` i `data/ablation_results.json`.