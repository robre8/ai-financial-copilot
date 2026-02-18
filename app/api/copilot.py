from fastapi import APIRouter
from pydantic import BaseModel
from app.services.mock_ai_service import MockAIService
from app.core.config import settings
from app.core.logger import setup_logger
from app.database import SessionLocal
from app.models import Question

router = APIRouter()
logger = setup_logger()

class QuestionRequest(BaseModel):
    question: str

def get_ai_service():
    if settings.USE_MOCK:
        logger.info("Using Mock AI Service")
        return MockAIService()
    logger.info("Using Real AI Service")
    return MockAIService()

@router.post("/copilot/ask")
def ask_copilot(request: QuestionRequest):
    logger.info(f"Received question: {request.question}")

    ai_service = get_ai_service()
    answer = ai_service.ask(request.question)

    # Guardar en base de datos
    db = SessionLocal()
    db_question = Question(
        question=request.question,
        answer=answer
    )
    db.add(db_question)
    db.commit()
    db.close()

    return {"answer": answer}

@router.get("/copilot/history")
def get_history():
    db = SessionLocal()
    questions = db.query(Question).all()
    db.close()

    return questions
