import os
import traceback
import requests
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
    logger.info(f"Starting PDF upload: {file.filename}")

    try:
        # Validar que es un PDF
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Guardar archivo temporalmente
        with open(file_location, "wb") as f:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="File is empty")
            f.write(content)
        
        logger.info(f"File saved: {file_location}")

        # Procesar documento
        logger.info("Processing document...")
        RAGService.process_document(file_location)
        logger.info("Document processing complete")

        # Guardar vector store (crítico)
        logger.info("Saving vector store...")
        RAGService.vector_store.save()
        logger.info("Vector store saved successfully")

        logger.info(f"PDF indexed successfully: {file.filename}")
        return {"message": "PDF indexed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
            logger.info(f"Temp file deleted: {file_location}")


@router.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    # Check API key first
    check_api_key()
    
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Processing question: {request.question[:50]}...")
        answer = RAGService.ask(request.question)
        logger.info("Question answered successfully")
        return QuestionResponse(answer=answer)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/debug/llm-raw")
def debug_llm_raw(request: DebugPromptRequest):
    """Return raw LLM client response for debugging. Use only for diagnostics."""
    check_api_key()

    try:
        from app.services.llm_service import HF_API_BASE, HF_HEADERS, HF_MODELS
        
        logger.info("Debug LLM raw: trying models with prompt: %s", request.prompt[:50])
        
        for model in HF_MODELS:
            url = f"{HF_API_BASE}/{model}"
            logger.info("Trying model: %s at %s", model, url)
            
            try:
                payload = {"inputs": request.prompt}
                response = requests.post(
                    url,
                    headers=HF_HEADERS,
                    json=payload,
                    timeout=30
                )
                
                logger.info("Model %s returned status: %d", model, response.status_code)
                
                if response.status_code == 200:
                    raw = response.json()
                    return {"raw": raw, "type": str(type(raw)), "status": response.status_code, "model": model}
                else:
                    logger.warning("Model %s failed with status %d, trying next", model, response.status_code)
                    continue
                    
            except Exception as model_err:
                logger.warning("Model %s exception: %s", model, repr(model_err))
                continue
        
        raise RuntimeError("All models exhausted without success")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Debug LLM raw failed: %s", tb)
        raise HTTPException(status_code=500, detail=f"Debug failed: {repr(e)}")
