from passlib.context import CryptContext
from app.services.supabase_service import supabase_service
from app.services.redis_service import redis_client
import uuid
import json

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    async def register_user(self, email, username, password):
        # Check if exists
        if await supabase_service.get_user_by_email(email):
            return None, "Email already registered"
        if await supabase_service.get_user_by_username(username):
            return None, "Username taken"
        
        hashed = self.get_password_hash(password)
        try:
            user = await supabase_service.create_user({
                "email": email, 
                "username": username, 
                "password_hash": hashed
            })
            if not user:
                 return None, "Failed to create user in database"
            return user, None
        except Exception as e:
            return None, str(e)

    async def login_user(self, email, password):
        user = await supabase_service.get_user_by_email(email)
        if not user:
            return None, "Invalid credentials"
        
        if not self.verify_password(password, user['password_hash']):
            return None, "Invalid credentials"
            
        # Create session
        session_id = str(uuid.uuid4())
        # Store in Redis (24h TTL)
        # Store user info (exclude hash)
        user_session = {k:v for k,v in user.items() if k != 'password_hash'}
        
        # Redis client wrapper usually has 'redis' property which is the async client
        if redis_client.redis:
            await redis_client.redis.setex(
                f"session:{session_id}", 
                86400, 
                json.dumps(user_session)
            )
            return session_id, None
        else:
            return None, "Redis unavailable"

    async def get_current_user(self, session_id):
        if not session_id or not redis_client.redis: return None
        data = await redis_client.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    async def logout_user(self, session_id):
        if not session_id or not redis_client.redis: return
        await redis_client.redis.delete(f"session:{session_id}")

auth_service = AuthService()
