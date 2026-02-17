from fastapi import FastAPI
from app.api import copilot
from app.core.logger import setup_logger
from fastapi.responses import JSONResponse
from fastapi.requests import Request

logger = setup_logger()

app = FastAPI()

app.include_router(copilot.router)

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