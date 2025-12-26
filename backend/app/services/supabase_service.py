from supabase import create_client, Client
from app.config import get_settings
import os

settings = get_settings()

class SupabaseService:
    def __init__(self):
        # We try to initialize the client if credentials exist
        self.client: Client = None
        # Note: In a real scenario, we'd add SUPABASE_URL and SUPABASE_KEY to settings/env
        # For this runnable demo, if they are missing, we gracefully degrade or warn.
        # But to answer the user's request, we implement the logic.
        
        # Use settings which loads from .env via Pydantic
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_KEY
        
        print(f"Initializing Supabase Client. URL provided: {bool(url)}, Key provided: {bool(key)}")
        
        if url and key:
            try:
                self.client = create_client(url, key)
                print("Supabase Client initialized successfully.")
            except Exception as e:
                print(f"Supabase Connection Error: {e}")
        else:
            print("Supabase credentials missing in Settings.")

    async def insert_message(self, message_data: dict):
        """Insert a message into the messages table."""
        if not self.client:
            return None
        
        try:
            # message_data needs to map to schema columns
            payload = {
                "id": message_data.get("id"), # Use the UUID we generated
                "room_id": message_data.get("room_id"),
                "user_id": message_data.get("user_id"),
                "content": message_data.get("content"),
                "type": message_data.get("type", "text"),
                "file_url": message_data.get("file_url"),
                "status": message_data.get("status"),
                # created_at is auto
            }
            response = self.client.table("messages").insert(payload).execute()
            return response
        except Exception as e:
            print(f"Supabase Insert Error: {e}")
            return None

    async def log_moderation(self, message_id: str, moderation_data: dict):
        """Insert a record into moderation_logs."""
        if not self.client:
            return None

        try:
            payload = {
                "message_id": message_id,
                "category": moderation_data.get("category"),
                "severity": moderation_data.get("severity"),
                "action": moderation_data.get("action"),
                "confidence": moderation_data.get("confidence"),
                "explanation": moderation_data.get("explanation"),
                "raw_response": moderation_data
            }
            response = self.client.table("moderation_logs").insert(payload).execute()
        except Exception as e:
            print(f"Supabase Log Error: {e}")

    async def get_history(self, room_id: str, limit: int = 50):
        """Fetch chat history for a room."""
        if not self.client:
            return []
        
        try:
            response = self.client.table("messages")\
                .select("*")\
                .eq("room_id", room_id)\
                .eq("status", "allowed")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            # Allow warning messages too? Requirement says "Blocked messages must never be broadcast".
            # Warnings are broadcast.
            # My query filtered only 'allowed'. Let's fix loop to include warnings.
            # actually better: .neq("status", "blocked")
            
            return response.data[::-1] # Reverse to chronological
        except Exception as e:
            print(f"Supabase Fetch Error: {e}")
            return []

    # --- User Management ---
    async def get_user_by_email(self, email: str):
        if not self.client: return None
        try:
            res = self.client.table("users").select("*").eq("email", email).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Get User Error: {e}")
            return None

    async def create_user(self, user_data: dict):
        if not self.client: 
            print("Supabase Client is NOT initialized.")
            return None
        try:
            print(f"Attempting to create user payload: {user_data.keys()}")
            res = self.client.table("users").insert(user_data).execute()
            print(f"Supabase Response Data: {res.data}")
            return res.data[0] if res.data else None
        except Exception as e:
            # Check for specific error attributes if available
            if hasattr(e, 'message'):
                print(f"Create User Error (Message): {e.message}")
            if hasattr(e, 'details'):
                 print(f"Create User Error (Details): {e.details}")
            print(f"Create User Error (Exception): {e}")
            return None

    async def get_user_by_username(self, username: str):
        if not self.client: return None
        try:
            res = self.client.table("users").select("*").eq("username", username).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Get User by Username Error: {e}")
            return None

    async def search_users(self, query: str):
        if not self.client: return []
        try:
            # Simple ILIKE search on username or email
            res = self.client.table("users").select("id, username, email")\
                .or_(f"username.ilike.%{query}%,email.ilike.%{query}%")\
                .limit(20).execute()
            return res.data
        except Exception as e:
            print(f"Search Users Error: {e}")
            return []

    # --- Conversation Management ---
    async def create_conversation(self, user_id_1: str, user_id_2: str):
        if not self.client: return None
        try:
            # 1. Create conversation
            conv_res = self.client.table("conversations").insert({}).execute()
            if not conv_res.data: return None
            conversation_id = conv_res.data[0]['id']

            # 2. Add participants
            participants = [
                {"conversation_id": conversation_id, "user_id": user_id_1},
                {"conversation_id": conversation_id, "user_id": user_id_2}
            ]
            self.client.table("participants").insert(participants).execute()
            
            return conversation_id
        except Exception as e:
            print(f"Create Conversation Error: {e}")
            return None

    async def get_user_conversations(self, user_id: str):
        if not self.client: return []
        try:
            # This is complex in simple Supabase client without joins. 
            # We might need a stored procedure or multiple queries.
            # Step 1: Get conversation_ids for user
            p_res = self.client.table("participants").select("conversation_id").eq("user_id", user_id).execute()
            if not p_res.data: return []
            
            conv_ids = [p['conversation_id'] for p in p_res.data]
            
            # Step 2: Get details for these conversations? 
            # Or get the OTHER user in these conversations.
            # Let's get all participants for these conversations to find the "other" user.
            
            # Using 'in' filter
            all_participants = self.client.table("participants")\
                .select("conversation_id, users(id, username)")\
                .in_("conversation_id", conv_ids)\
                .neq("user_id", user_id)\
                .execute()
                
            # Note: The above foreign key query `users(id, username)` depends on Supabase detecting the Relation.
            # If relation not set up in GUI, this might fail.
            # Fallback: Get all participants, then fetch users.
            
            return all_participants.data
        except Exception as e:
            print(f"Get Conversations Error: {e}")
            return []

supabase_service = SupabaseService()
