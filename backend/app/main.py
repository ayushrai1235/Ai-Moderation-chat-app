from fastapi import FastAPI
import json
from app.services.redis_service import redis_client
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB Tables
    try:
        from app.db.init_db import init_db
        init_db()
    except Exception as e:
        print(f"DB Init Warning: {e}")

    # Startup
    print("Starting up...")
    try:
        await redis_client.redis.ping()
        print("Redis connected.")
    except Exception as e:
        print(f"Redis connection warning: {e}")
        
    yield
    # Shutdown
    print("Shutting down...")
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.conversations import router as conversations_router

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI Moderation Chat App Backend is running"}

@app.get("/health")
async def health_check():
    try:
        await redis_client.redis.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return {"status": "ok", "redis": redis_status}

from app.services.websocket_manager import manager
from app.services.moderation_pipeline import moderation_pipeline
from app.services.auth_service import auth_service
from app.api.deps import get_current_user
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, Header

@app.websocket("/ws/{room_id}/{token}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str):
    # Validate Session
    user = await auth_service.get_current_user(token)
    if not user:
        await websocket.close(code=4003)
        return
        
    user_id = user['id']

    await manager.connect(websocket, room_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Parse message
            try:
                message_data = json.loads(data)
            except:
                message_data = {"content": data}
            
            message_data['user_id'] = user_id
            message_data['room_id'] = room_id
            
            # Process through pipeline
            await moderation_pipeline.process_message(message_data, room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

@app.get("/api/history/{room_id}")
async def get_chat_history(room_id: str):
    from app.services.supabase_service import supabase_service
    history = await supabase_service.get_history(room_id)
    return history


@app.get("/api/moderation/logs")
async def get_moderation_logs():
    # Fetch from Redis queue "admin:flagged_messages"
    # We want to peek, not pop, or get all.
    # Redis lists: lrange
    logs = await redis_client.redis.lrange("admin:flagged_messages", 0, -1)
    return [json.loads(log) for log in logs]

@app.post("/api/upload/sign")
async def sign_upload(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Return signature for Cloudinary upload
    from app.services.cloudinary_service import cloudinary_service
    import time
    
    timestamp = int(time.time())
    params = {
        "timestamp": timestamp,
        "folder": "chat_app"
    }
    signature = cloudinary_service.generate_signature(params)
    
    return {
        "signature": signature,
        "timestamp": timestamp,
        "api_key": cloudinary_service.settings.CLOUDINARY_API_KEY,
        "cloud_name": cloudinary_service.settings.CLOUDINARY_CLOUD_NAME,
        "folder": "chat_app"
    }

