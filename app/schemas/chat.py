from pydantic import BaseModel
from typing import List, Optional

from typing import Optional

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class Source(BaseModel):
    source: str
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    session_id: str
    debug_info: Optional[dict] = None
