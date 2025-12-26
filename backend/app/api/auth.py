from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(req: RegisterRequest):
    user, error = await auth_service.register_user(req.email, req.username, req.password)
    if error:
        print(f"Registration Error: {error}") # Debug log
        raise HTTPException(status_code=400, detail=error)
    return {"message": "User registered successfully", "user_id": user['id']}

@router.post("/login")
async def login(req: LoginRequest):
    session_id, error = await auth_service.login_user(req.email, req.password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return {"session_id": session_id, "token_type": "bearer"}

@router.post("/logout")
async def logout(authorization: str = Header(None)):
    if not authorization:
        return {"message": "Logged out"}
    
    token = authorization.split(" ")[1] if " " in authorization else authorization
    await auth_service.logout_user(token)
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.split(" ")[1] if " " in authorization else authorization
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
