from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.supabase_service import supabase_service
from app.services.supabase_service import supabase_service
from app.services.auth_service import auth_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search")
async def search_users(
    q: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    users = await supabase_service.search_users(q)
    # Filter out current user from results if needed, or handle in frontend
    return [u for u in users if u['id'] != current_user['id']]
