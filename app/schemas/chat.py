from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str

class Source(BaseModel):
    source: str
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
