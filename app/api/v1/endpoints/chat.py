from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service_instance, RAGService

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def get_chat_answer(
    request: ChatRequest,
    # Use the singleton instance for efficiency
    rag_service: RAGService = Depends(lambda: rag_service_instance)
):
    """
    Endpoint to get an answer from the RAG chatbot.
    """
    return rag_service.get_answer(query=request.query)
