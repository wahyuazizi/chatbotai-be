from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Chatbot AI Backend",
    version="1.0.0",
    description="Backend for a RAG-based AI Chatbot with FastAPI, Supabase, and Azure AI.",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "ok", "user_agent": settings.USER_AGENT}
