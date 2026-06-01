from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.query import answer_question

router = APIRouter(prefix="/query", tags=["query"])


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = answer_question(
            question=request.question,
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result