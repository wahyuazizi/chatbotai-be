from typing import Optional, Tuple, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel # Added BaseModel
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service_instance, RAGService
from app.services.chat_history_service import chat_history_service_instance, ChatHistoryService
from app.utils.security import get_optional_current_user_context

router = APIRouter()

# Define a new schema for chat messages in history
class HistoryMessage(BaseModel):
    role: str
    content: str

# Define a new response model for chat history
class ChatHistoryResponse(BaseModel):
    messages: List[HistoryMessage]
    session_id: str

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

@router.get("/history", response_model=ChatHistoryResponse) # Changed response_model
async def get_chat_history(
    session_id: Optional[str] = None, # Allow session_id as query param for anonymous users
    history_service: ChatHistoryService = Depends(lambda: chat_history_service_instance),
    user_context: Tuple[Optional[str], Optional[str]] = Depends(get_optional_current_user_context)
) -> ChatHistoryResponse: # Changed response_model
    user_id, access_token = user_context
    print(f"DEBUG: get_chat_history endpoint hit! session_id: {session_id}, user_id: {user_id}")
    
    # Prioritize user_id for logged-in users, otherwise use session_id
    if user_id:
        history_messages = history_service.get_history(session_id=session_id, user_id=user_id, access_token=access_token)
    elif session_id:
        history_messages = history_service.get_history(session_id=session_id, user_id=None, access_token=access_token)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either session_id or a valid authentication token must be provided."
        )
    print(f"DEBUG: Returning history_messages: {history_messages}")
    return ChatHistoryResponse(messages=history_messages, session_id=session_id or "N/A") # Changed return

@router.post("/clear")
async def clear_chat_history(
    session_id: str = None, # Allow session_id in body for anonymous users
    history_service: ChatHistoryService = Depends(lambda: chat_history_service_instance),
    user_context: Tuple[Optional[str], Optional[str]] = Depends(get_optional_current_user_context)
):
    user_id, access_token = user_context

    if user_id:
        await history_service.clear_history(user_id=user_id, access_token=access_token)
        return {"message": "Chat history cleared for authenticated user."}
    elif session_id:
        await history_service.clear_history(session_id=session_id, access_token=access_token)
        return {"message": "Chat history cleared for anonymous session."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either session_id or a valid authentication token must be provided to clear history."
        )
