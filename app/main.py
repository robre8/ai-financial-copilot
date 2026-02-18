from fastapi import FastAPI
from app.api import copilot
from app.core.logger import setup_logger
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.database import engine
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Question


logger = setup_logger()

app = FastAPI(title="AI Financial Copilot")

app.include_router(copilot.router)

@app.get("/")
def root():
    return {
        "message": "AI Financial Copilot API",
        "status": "running",
        "docs": "/docs"
    }


@app.on_event("startup")
def startup_event():
    logger.info("AI Financial Copilot API started successfully.")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Financial Copilot",
        "version": "1.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }
    )

@app.get("/db-test")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": "connected"}


@app.get("/save-test")
def save_test():
    db = SessionLocal()
    new_question = Question(
        question="Test question",
        answer="Test answer"
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    db.close()

    return {"message": "Saved", "id": new_question.id}
