from typing import Optional, Tuple
import uuid
from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service_instance, RAGService
from app.services.chat_history_service import chat_history_service_instance, ChatHistoryService
from app.utils.security import get_optional_current_user_context

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def get_chat_answer(
    request: ChatRequest,
    rag_service: RAGService = Depends(lambda: rag_service_instance),
    history_service: ChatHistoryService = Depends(lambda: chat_history_service_instance),
    user_context: Tuple[Optional[str], Optional[str]] = Depends(get_optional_current_user_context)
) -> ChatResponse:
    user_id, access_token = user_context
    """
    Endpoint to get an answer from the RAG chatbot.
    """
    # 1. Get or create a session ID
    session_id = request.session_id or str(uuid.uuid4())

    # 2. Get the answer from the RAG service, providing the session and user context
    response = rag_service.get_answer(
        query=request.query, 
        session_id=session_id, 
        user_id=user_id
    )

    # 3. Save the user's query and the AI's answer to the history
    history_service.add_message(
        session_id=session_id, 
        role='user', 
        content=request.query, 
        user_id=user_id,
        access_token=access_token # Pass access_token
    )
    history_service.add_message(
        session_id=session_id, 
        role='assistant', 
        content=response.answer, 
        user_id=user_id,
        access_token=access_token # Pass access_token
    )

    # 4. Include the session ID in the final response
    response.session_id = session_id
    
    return response
