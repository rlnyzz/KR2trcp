from fastapi import APIRouter, HTTPException, status, Cookie, Response
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(tags=["5.1 - Cookie аутентификация"])

users_db = {
    "user123": {
        "password": "password123", 
        "name": "John Doe", 
        "email": "john@example.com"
    },
    "alice": {
        "password": "alicepass", 
        "name": "Alice Smith", 
        "email": "alice@example.com"
    }
}

sessions = {}

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
    "/login",
    summary="Вход в систему",
    description="Аутентификация пользователя и установка session_token cookie"
)
async def login(login_data: LoginRequest, response: Response):
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    session_token = str(uuid.uuid4())
    sessions[session_token] = {
        "username": login_data.username,
        "user_info": user
    }
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True, 
        max_age=3600,   
        secure=False,   
        samesite="lax"  
    )
    
    return {
        "message": "Login successful",
        "username": login_data.username
    }

@router.get(
    "/user",
    summary="Получить информацию о пользователе",
    description="Защищенный маршрут, требующий валидной сессии"
)
async def get_user(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token missing"
        )
    
    if session_token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    session_data = sessions[session_token]
    return {
        "username": session_data["username"],
        "name": session_data["user_info"]["name"],
        "email": session_data["user_info"]["email"]
    }

@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет session_token cookie и завершает сессию"
)
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None)
):
    if session_token and session_token in sessions:
        del sessions[session_token]
    
    response.delete_cookie(key="session_token")
    return {"message": "Logout successful"}