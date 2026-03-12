from fastapi import APIRouter, HTTPException, status, Cookie, Response
from pydantic import BaseModel
from typing import Optional
import uuid
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

router = APIRouter(tags=["5.2 - Подписанные cookie"])

SECRET_KEY = "your-secret-key-here-change-in-production-8a7f6e5d4c3b2a1"
serializer = URLSafeTimedSerializer(SECRET_KEY)

users_db = {
    "user123": {
        "password": "password123", 
        "name": "John Doe", 
        "email": "john@example.com",
        "user_id": str(uuid.uuid4())
    },
    "alice": {
        "password": "alicepass", 
        "name": "Alice Smith", 
        "email": "alice@example.com",
        "user_id": str(uuid.uuid4())
    }
}

class LoginRequest(BaseModel):
    """Модель запроса на логин"""
    username: str
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "username": "user123",
                "password": "password123"
            }
        }

@router.post(
    "/login/v2",
    summary="Вход с подписанным токеном",
    description="Аутентификация с установкой подписанного session_token cookie"
)
async def login_v2(login_data: LoginRequest, response: Response):
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
 
    user_id = user.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        user["user_id"] = user_id
    

    signed_token = serializer.dumps(user_id)
  
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=3600,  
        secure=False,
        samesite="lax"
    )
    
    return {
        "message": "Login successful", 
        "user_id": user_id
    }

@router.get(
    "/profile",
    summary="Профиль с проверкой подписи",
    description="Защищенный маршрут с проверкой подписи session_token"
)
async def get_profile(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token missing"
        )
    
    try:
        user_id = serializer.loads(session_token, max_age=3600)

        username = None
        user_info = None
        for uname, data in users_db.items():
            if data.get("user_id") == user_id:
                username = uname
                user_info = data
                break
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "user_id": user_id,
            "username": username,
            "name": user_info["name"],
            "email": user_info["email"],
            "message": "Profile accessed successfully with signature verification"
        }
        
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session signature - possible tampering detected"
        )