
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from app.core.config import settings

class ChatHistoryService:
    def __init__(self):
        # Initialize with anon key for general use, will be re-initialized with user token if provided
        try:
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logging.info("Successfully connected to Supabase with anon key.")
        except Exception as e:
            logging.error(f"Failed to connect to Supabase: {e}")
            self.supabase = None

    def _get_authenticated_supabase_client(self, access_token: Optional[str] = None) -> Client:
        """Returns a Supabase client, authenticated with the provided access_token if available."""
        # Always start with the anon key client
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        if access_token:
            logging.info("Attempting to authenticate Supabase client with access token.")
            try:
                # Set the access token for the client to make authenticated requests
                client.postgrest.auth(access_token)
                logging.info("Supabase client authenticated with access token.")
            except Exception as e:
                logging.error(f"Failed to set access token on Supabase client: {e}")
        else:
            logging.info("No access token provided. Using anonymous Supabase client.")
        return client

    def add_message(self, session_id: str, role: str, content: str, user_id: Optional[str] = None, access_token: Optional[str] = None):
        """Adds a new message to the chat history in Supabase."""
        supabase_client = self._get_authenticated_supabase_client(access_token)
        if not supabase_client:
            logging.error("Supabase client not available. Cannot add message.")
            return

        try:
            message_data = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "user_id": user_id
            }
            supabase_client.table("chat_messages").insert(message_data).execute()
            logging.info(f"Message added to Supabase. User ID: {user_id}, Session ID: {session_id}")
        except Exception as e:
            logging.error(f"Error adding message to Supabase: {e}")

    def get_history(self, session_id: str, user_id: Optional[str] = None, access_token: Optional[str] = None, limit: int = 5) -> List[Dict[str, str]]: # Changed return type
        """
        Retrieves chat history from the last 24 hours and returns it as a list of message dictionaries.
        It prioritizes fetching by user_id if available, otherwise falls back to session_id.
        Limits the number of messages returned to the 'limit' parameter (default 5).
        """
        supabase_client = self._get_authenticated_supabase_client(access_token)
        if not supabase_client:
            logging.error("Supabase client not available. Cannot get history.")
            return [] # Return empty list instead of error string

        try:
            twenty_four_hours_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            
            query = self.supabase.table("chat_messages").select("role, content")

            # Prioritize user_id for logged-in users
            if user_id:
                query = query.eq("user_id", user_id)
            else:
                # Fallback to session_id for anonymous users
                query = query.eq("session_id", session_id)
            
            # Order by created_at descending to get the most recent messages, then limit
            response = query.gte("created_at", twenty_four_hours_ago).order("created_at", desc=True).limit(limit).execute()

            if not response.data:
                return [] # Return empty list

            # Sort the messages chronologically before returning
            ordered_messages = sorted(response.data, key=lambda x: x['created_at'])

            # Return list of dicts with only role and content
            return [{"role": msg['role'], "content": msg['content']} for msg in ordered_messages]
        except Exception as e:
            logging.error(f"Error getting history from Supabase: {e}")
            return [] # Return empty list on error

    def clear_history(self, session_id: Optional[str] = None, user_id: Optional[str] = None, access_token: Optional[str] = None):
        """
        Clears chat history for a given session_id or user_id.
        Prioritizes user_id if provided.
        """
        supabase_client = self._get_authenticated_supabase_client(access_token)
        if not supabase_client:
            logging.error("Supabase client not available. Cannot clear history.")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Supabase client not available.")

        try:
            if user_id:
                response = supabase_client.table("chat_messages").delete().eq("user_id", user_id).execute()
                logging.info(f"Cleared history for user_id: {user_id}. Response: {response.data}")
            elif session_id:
                response = supabase_client.table("chat_messages").delete().eq("session_id", session_id).execute()
                logging.info(f"Cleared history for session_id: {session_id}. Response: {response.data}")
            else:
                raise ValueError("Either session_id or user_id must be provided to clear history.")
        except Exception as e:
            logging.error(f"Error clearing history from Supabase: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to clear history: {e}")

# Singleton instance
chat_history_service_instance = ChatHistoryService()
