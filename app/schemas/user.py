from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")

class UserLogin(UserBase):
    password: str = Field(..., example="strongpassword123")

class UserResponse(UserBase):
    id: str
    
    class Config:
        from_attributes = True
