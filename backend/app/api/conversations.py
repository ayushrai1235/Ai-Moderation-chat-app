from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.supabase_service import supabase_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])

class CreateConversationRequest(BaseModel):
    target_user_id: str

@router.get("")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get raw conversation data
    # Logic in supabase_service returns list of participants rows where user_id != current_user
    # row: { conversation_id, users: {id, username} }
    raw_data = await supabase_service.get_user_conversations(current_user['id'])
    
    # Format for frontend
    # Expected: [{ id: 'conv_id', name: 'Other User Name', ... }]
    conversations = []
    for item in raw_data:
        try:
            other_user = item.get('users')
            # If relation works:
            if other_user:
                 conversations.append({
                    "id": item['conversation_id'],
                    "name": other_user['username'],
                    "other_user_id": other_user['id']
                })
        except Exception as e:
            print(f"Error parsing conversation: {e}")
            
    return conversations

@router.post("")
async def create_conversation(
    req: CreateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if req.target_user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")

    # TODO: Check if conversation already exists? 
    # For now, simplistic approach: create new or return existing.
    # We don't have a "get_existing_conversation" method yet.
    # Let's just create one. (It might result in duplicates if we don't check, 
    # but schema doesn't enforce unique participants pair currently).
    
    conv_id = await supabase_service.create_conversation(current_user['id'], req.target_user_id)
    if not conv_id:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
        
    return {"conversation_id": conv_id}
