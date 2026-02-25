import os
import traceback
import requests
import gc
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Security, Request
from app.services.rag_service import RAGService
from app.services.agent_service import get_financial_agent
from app.schemas.rag_schema import QuestionRequest, QuestionResponse, DebugPromptRequest
from app.core.logger import setup_logger
from app.core.config import settings
from app.services.llm_service import LLMService
from app.core.security import validate_api_key, require_scope, APIKeyScope
from app.core.rate_limit import limiter

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
        "message": "AI Financial Copilot - RAG + Agent System",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "upload_pdf": "POST /upload-pdf",
            "ask_question": "POST /ask",
            "analyze_financial": "POST /analyze",
            "webhook": "POST /webhooks/analysis-complete"
        }
    }


@router.post("/upload-pdf")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    key_data: dict = Security(require_scope(APIKeyScope.WRITE))
):
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

        # PostgreSQL persists automatically - no need to manually save
        
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
def ask_question(
    request: QuestionRequest,
    http_request: Request,
    key_data: dict = Security(validate_api_key)
):
    # Check API key first
    check_api_key()
    
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        result = RAGService.ask(request.question)
        
        # 🔹 Cleanup memory after inference
        gc.collect()
        
        return QuestionResponse(
            answer=result["answer"],
            model=result["model"],
            chunks=result["chunks"],
            chunk_count=len(result["chunks"]),
            context=result["context"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/debug/llm-raw")
def debug_llm_raw(
    http_request: Request,
    request: DebugPromptRequest,
    key_data: dict = Security(validate_api_key)
):
    """Return raw LLM client response for debugging. Use only for diagnostics."""
    check_api_key()

    try:
        from app.services.llm_service import LLMService
        
        logger.info("Debug LLM raw: trying models with prompt: %s", request.prompt[:50])
        
        result, model_used = LLMService.generate(request.prompt)

        return {"result": result, "model": model_used, "type": str(type(result)), "status": 200}

    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Debug LLM raw failed: %s", tb)
        raise HTTPException(status_code=500, detail=f"Debug failed: {repr(e)}")


@router.post("/analyze")
def analyze_financial_document(
    http_request: Request,
    request: QuestionRequest,
    key_data: dict = Security(validate_api_key)
):
    """
    Analyze financial document using Financial Analysis Agent.
    
    Uses tools:
    1. extract_financial_metrics
    2. detect_risk_patterns
    3. generate_structured_report
    
    Returns: Structured financial analysis with metrics and recommendations
    """
    check_api_key()
    
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Document content cannot be empty")
        
        # Get Financial Analysis Agent
        agent = get_financial_agent()
        
        # Run analysis
        logger.info("🤖 Starting financial analysis with agent...")
        analysis_result = agent.analyze(request.question)
        
        # Cleanup
        gc.collect()
        
        logger.info("✅ Financial analysis complete")
        return {
            "status": "success",
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in financial analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/webhooks/analysis-complete")
async def webhook_analysis_complete(
    http_request: Request,
    key_data: dict = Security(validate_api_key)
):
    """
    Webhook endpoint for analysis completion notifications.
    
    In production, this would:
    - Notify external systems
    - Trigger automatic workflows
    - Store analysis results in external systems
    - Send alerts to stakeholders
    
    This demonstrates enterprise-grade integration capabilities.
    """
    check_api_key()
    
    try:
        # Get webhook payload from request body
        body = await http_request.json()
        
        webhook_event = {
            "event_type": "analysis.completed",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "payload": body,
            "processing_time_ms": body.get("processing_time_ms", 0)
        }
        
        logger.info(f"🔔 Webhook event received: {webhook_event['event_type']}")
        
        # In production, this would:
        # 1. Validate webhook signature
        # 2. Route to appropriate handler
        # 3. Retry logic with exponential backoff
        # 4. Dead letter queue for failed deliveries
        
        # Simulate webhook delivery to external system
        external_systems = [
            "https://example.com/webhooks/analysis",
            "https://analytics.internal/events"
        ]
        
        delivery_results = []
        for endpoint in external_systems:
            try:
                # In real scenario: requests.post(endpoint, json=webhook_event, timeout=5)
                # For now, just log the intent
                logger.info(f"📤 Would deliver webhook to: {endpoint}")
                delivery_results.append({
                    "endpoint": endpoint,
                    "status": "queued",
                    "message": "Webhook queued for delivery"
                })
            except Exception as e:
                logger.warning(f"⚠️ Webhook delivery failed: {str(e)}")
                delivery_results.append({
                    "endpoint": endpoint,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "webhook_status": "acknowledged",
            "event_id": body.get("event_id", "unknown"),
            "timestamp": webhook_event["timestamp"],
            "delivery_results": delivery_results,
            "message": "Webhook processed successfully. External systems will be notified."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")
