from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.clients import supabase_client
from app.services.auth_service import AuthService
from app.schemas.user import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    auth_service = AuthService(supabase_client)
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse(id=user.id, email=user.email, role=user.user_metadata.get("role", "user"))

def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    # Add logic here if you need to check if a user is active (e.g., email confirmed)
    return current_user

def has_role(required_roles: list[str]):
    def role_checker(current_user: UserResponse = Depends(get_current_active_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
