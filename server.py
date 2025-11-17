from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from core import load_kb, append_kb_entry, generate_answer

app = FastAPI(title="Kosmo Chatbot API", version="1.0.0")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question in Kinyarwanda")


class ChatResponse(BaseModel):
    answer: str


class KBEntry(BaseModel):
    question: str
    answer: str
    tags: Optional[str] = ""


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    df = load_kb()
    answer = generate_answer(body.query, df)
    return ChatResponse(answer=answer)


@app.get("/kb")
async def list_kb(limit: int = 100, offset: int = 0) -> dict:
    df = load_kb()
    end = min(offset + limit, len(df))
    rows = df.iloc[offset:end].to_dict(orient="records")
    return {"total": len(df), "items": rows}


@app.post("/kb")
async def add_kb(entry: KBEntry) -> dict:
    if not entry.question.strip() or not entry.answer.strip():
        raise HTTPException(status_code=400, detail="question and answer are required")
    append_kb_entry(entry.question, entry.answer, entry.tags or "")
    return {"ok": True}
