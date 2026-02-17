from fastapi import APIRouter
from pydantic import BaseModel
from app.services.mock_ai_service import MockAIService
from app.core.config import settings
from app.core.logger import setup_logger

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
    return {"answer": answer}
