import os
from fastapi import APIRouter, UploadFile, File
from app.services.rag_service import RAGService
from app.schemas.rag_schema import QuestionRequest, QuestionResponse

router = APIRouter()


@router.get("/")
def root():
    """Health check and welcome endpoint"""
    return {
        "message": "AI Financial Copilot - RAG System",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "upload_pdf": "POST /upload-pdf",
            "ask_question": "POST /ask"
        }
    }


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"

    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())

        RAGService.process_document(file_location)

        return {"message": "PDF indexed successfully"}

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)


@router.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    answer = RAGService.ask(request.question)
    return QuestionResponse(answer=answer)
