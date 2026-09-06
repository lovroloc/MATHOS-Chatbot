from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time, uuid, json, os

from hybrid_search import hybrid_search
from generate import answer

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request





app = FastAPI(title="Mathos Chatbot API")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # za razvoj; u produkciji suzi na mathos.unios.hr
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- modeli ---

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class Source(BaseModel):
    title: str
    url: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    session_id: str
    latency_ms: int

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# --- logiranje ---

LOG_PATH = "data/query_log.jsonl"
SESSIONS = {}          # session_id -> [{"role": ..., "content": ...}]
MAX_HISTORY = 8
os.makedirs("data", exist_ok=True)

def log_query(entry):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# --- endpointi ---

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search")
@limiter.limit("60/minute")
def search(request: Request, req: SearchRequest):
    """Samo retrieval, bez LLM-a. Koristi eval runner."""
    t0 = time.time()
    try:
        results = hybrid_search(req.query, top_n=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pretrage: {e}")

    return {
        "chunks": [
            {"chunk_id": r[0][0], "title": r[0][1], "url": r[0][2],
            "text": r[0][3], "score": r[1], "raw_score": r[2]}
            for r in results
        ],
        "latency_ms": int((time.time() - t0) * 1000),
    }

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("15/minute")
def chat(request: Request, req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Prazna poruka.")

    session_id = req.session_id or str(uuid.uuid4())
    t0 = time.time()
    history = SESSIONS.get(session_id, [])

    try:
        text, sources = answer(req.message, history=history)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servis trenutno nedostupan: {e}")

    history = history + [
        {"role": "korisnik", "content": req.message},
        {"role": "asistent", "content": text},
    ]
    SESSIONS[session_id] = history[-MAX_HISTORY:]

    latency = int((time.time() - t0) * 1000)

    log_query({
        "timestamp": time.time(),
        "session_id": session_id,
        "question": req.message,
        "answer": text,
        "sources": [{"title": t, "url": u} for t, u in sources],
        "latency_ms": latency,
    })

    return ChatResponse(
        answer=text,
        sources=[Source(title=t, url=u) for t, u in sources],
        session_id=session_id,
        latency_ms=latency,
    )