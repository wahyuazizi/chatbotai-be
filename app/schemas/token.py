from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = None

class TokenData(BaseModel):
    user_id: str | None = None
    role: Optional[str] = None
