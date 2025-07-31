from typing import Optional, Tuple
import jwt
import logging
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.clients import supabase_client
from app.services.auth_service import AuthService
from app.schemas.user import UserResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

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

async def get_optional_current_user_context(request: Request) -> Tuple[Optional[str], Optional[str]]:
    """
    A dependency that tries to extract a user ID and the full JWT token from the Authorization header.
    If the token is missing, invalid, or expired, it returns (None, None) instead of failing.
    This allows endpoints to serve both authenticated and anonymous users.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        logger.info("Authorization header missing. User is anonymous.")
        return None, None

    # Extract token string (remove "Bearer ")
    token_string = auth_header.split(" ")[-1]
    
    try:
        payload = jwt.decode(
            token_string,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True, "verify_aud": True},
            audience="authenticated"
        )
        user_id = payload.get("sub") # "sub" claim usually holds the user ID (UID)
        return user_id, token_string
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        return None, None
    except jwt.PyJWTError as e: # Catch all PyJWT errors specifically
        logger.error(f"Invalid JWT token (PyJWTError): {e}")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred during token processing: {type(e).__name__}: {e}")
        return None, None
