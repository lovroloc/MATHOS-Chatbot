import time
from hybrid_search import hybrid_search

queries = [
    "kad je referada otvorena",
    "koliko ECTS-a nosi Diferencijalni račun",
    "što je kolegij M145",
    "kontakt Kristian Sabo",
    "koji kolegiji se bave strojnim učenjem",
]

configs = [
    ("Hibridni k=5",                    {"top_n": 5}),
    ("Hibridni k=3 + rerank pool=20",   {"top_n": 3, "rerank": True, "rerank_pool": 20}),
    ("Hibridni k=3 + rerank pool=8",    {"top_n": 3, "rerank": True, "rerank_pool": 8}),
    ("Hibridni k=3 + rerank pool=5",    {"top_n": 3, "rerank": True, "rerank_pool": 5}),
]

for label, kwargs in configs:
    hybrid_search(queries[0], **kwargs)          # zagrijavanje
    times = []
    for q in queries:
        t0 = time.time()
        hybrid_search(q, **kwargs)
        times.append((time.time() - t0) * 1000)
    avg = sum(times) / len(times)
    print(f"{label:<26} {avg:>7.0f} ms  (min {min(times):.0f}, max {max(times):.0f})")