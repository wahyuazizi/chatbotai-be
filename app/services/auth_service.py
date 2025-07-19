from fastapi import HTTPException, status
from supabase import Client as SupabaseClient
from gotrue.errors import AuthApiError

from app.schemas.user import UserCreate, UserLogin

class AuthService:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client

    def register_user(self, user_data: UserCreate):
        try:
            user = self.supabase_client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
            })
            return user
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def login_user(self, user_data: UserLogin):
        try:
            session = self.supabase_client.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password,
            })
            return session
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message or "Invalid credentials",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def get_user_from_token(self, token: str):
        try:
            user = self.supabase_client.auth.get_user(token)
            return user
        except AuthApiError:
            return None
        except Exception:
            return None
