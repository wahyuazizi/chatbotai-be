from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Chatbot AI Backend",
    version="1.0.0",
    description="Backend for a RAG-based AI Chatbot with FastAPI, Supabase, and Azure AI.",
)

origins = [
    "http://localhost:3000",  # Allow requests from your frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "ok", "user_agent": settings.USER_AGENT}
