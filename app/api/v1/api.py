from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat, ingest

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
api_router.include_router(ingest.router, prefix="/data", tags=["Data Management"])
