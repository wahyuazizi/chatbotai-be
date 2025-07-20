from fastapi import APIRouter, Depends, HTTPException, status
from app.core.clients import supabase_client
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, auth_service: AuthService = Depends(lambda: AuthService(supabase_client))):
    """
    Register a new user.
    """
    user = auth_service.register_user(user_data)
    # Supabase handles email confirmation, so we just return a success message
    if user:
        return {"message": "Registration successful. Please check your email to confirm your account."}
    # The service raises HTTPException on failure, but as a fallback:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not register user.")


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, auth_service: AuthService = Depends(lambda: AuthService(supabase_client))):
    """
    Login for existing users.
    """
    session_response = auth_service.login_user(user_data)
    if session_response.session and session_response.session.access_token:
        user_role = session_response.user.role if session_response.user else "user"
        return Token(access_token=session_response.session.access_token, token_type="bearer", role=user_role)
    # The service raises HTTPException on failure, but as a fallback:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed.")
