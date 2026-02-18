import os
import traceback
import requests
import gc
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.rag_service import RAGService
from app.schemas.rag_schema import QuestionRequest, QuestionResponse, DebugPromptRequest
from app.core.logger import setup_logger
from app.core.config import settings
from app.services.llm_service import LLMService

router = APIRouter()
logger = setup_logger()


def check_api_key():
    """Ensure API key is configured"""
    try:
        settings.validate()
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


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
    # Check API key first
    check_api_key()
    
    file_location = f"temp_{file.filename}"
    logger.info(f"Processing PDF: {file.filename}")

    try:
        # Validar que es un PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Guardar archivo temporalmente
        with open(file_location, "wb") as f:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="File is empty")
            f.write(content)
            del content  # Clear memory immediately
        
        # Procesar documento
        RAGService.process_document(file_location)

        # Guardar vector store (crítico)
        RAGService.vector_store.save()
        
        # 🔹 Explicit memory cleanup
        gc.collect()

        logger.info(f"PDF indexed: {file.filename}")
        return {"message": "PDF indexed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

    finally:
        # 🔹 Always cleanup temp file
        if os.path.exists(file_location):
            os.remove(file_location)
        gc.collect()


@router.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    # Check API key first
    check_api_key()
    
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        answer = RAGService.ask(request.question)
        
        # 🔹 Cleanup memory after inference
        gc.collect()
        
        return QuestionResponse(answer=answer)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/debug/llm-raw")
def debug_llm_raw(request: DebugPromptRequest):
    """Return raw LLM client response for debugging. Use only for diagnostics."""
    check_api_key()

    try:
        from app.services.llm_service import LLMService
        
        logger.info("Debug LLM raw: trying models with prompt: %s", request.prompt[:50])
        
        result = LLMService.generate(request.prompt)
        
        return {"result": result, "type": str(type(result)), "status": 200}

    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Debug LLM raw failed: %s", tb)
        raise HTTPException(status_code=500, detail=f"Debug failed: {repr(e)}")
