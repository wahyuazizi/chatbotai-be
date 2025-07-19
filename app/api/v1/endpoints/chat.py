from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service
from app.utils.security import get_current_user
from gotrue.types import User

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def get_chat_response(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get a response from the chatbot. User must be authenticated.
    """
    return rag_service.get_answer(chat_request.query)
