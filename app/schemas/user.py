from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")
    role: Optional[str] = "user" # Default role for new registrations

class UserLogin(UserBase):
    password: str = Field(..., example="strongpassword123")

class UserResponse(UserBase):
    id: str
    role: str = "user" # Default role if not found, though it should be set
    
    class Config:
        from_attributes = True
