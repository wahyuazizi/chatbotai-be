from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def get_chat_answer(
    request: ChatRequest,
    rag_service: RAGService = Depends(RAGService),
    # current_user: dict = Depends(get_current_user) # Uncomment for authentication
):
    """
    Endpoint to get an answer from the RAG chatbot.
    """
    return rag_service.get_answer(query=request.query)