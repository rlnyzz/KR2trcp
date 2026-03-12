from fastapi import APIRouter, HTTPException, status, Response, Request
from pydantic import BaseModel
from typing import Optional, Tuple
import uuid
import time
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, BadSignature

router = APIRouter(tags=["5.3 - Динамические сессии"])

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

class SessionManager:
    SESSION_DURATION = 300  
    RENEWAL_THRESHOLD = 180  
    
    @classmethod
    def create_session_token(cls, user_id: str) -> str:
        timestamp = int(time.time())
        data = f"{user_id}.{timestamp}"
        return serializer.dumps(data)
    
    @classmethod
    def verify_and_refresh_session(cls, token: str, current_time: int = None) -> Tuple[Optional[str], bool, Optional[str]]:
        if current_time is None:
            current_time = int(time.time())
        
        try:
            data = serializer.loads(token, max_age=None)
            
            parts = data.split('.')
            if len(parts) != 2:
                return None, False, None
                
            user_id, last_activity = parts
            last_activity = int(last_activity)
            
            time_passed = current_time - last_activity
            
            if time_passed > cls.SESSION_DURATION:
                print(f"Session expired: {time_passed}s > {cls.SESSION_DURATION}s")
                return None, False, None
            
            needs_refresh = cls.RENEWAL_THRESHOLD <= time_passed < cls.SESSION_DURATION
            
            if needs_refresh:
                new_token = cls.create_session_token(user_id)
                print(f"Session refreshed at {time_passed}s")
                return user_id, True, new_token
            else:
                print(f"Session valid, no refresh needed ({time_passed}s passed)")
                return user_id, False, None
                
        except BadSignature:
            print("Bad signature detected")
            return None, False, None
        except (ValueError, AttributeError) as e:
            print(f"Error parsing session: {e}")
            return None, False, None

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login/v3", summary="Вход с динамической сессией")
async def login_v3(login_data: LoginRequest, response: Response):
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_id = user.get("user_id")
    
    session_token = SessionManager.create_session_token(user_id)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=SessionManager.SESSION_DURATION,
        secure=False,
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "user_id": user_id,
        "session_duration": SessionManager.SESSION_DURATION,
        "renewal_threshold": SessionManager.RENEWAL_THRESHOLD
    }

@router.get("/profile/v3", summary="Профиль с динамическим продлением")
async def get_profile_v3(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    current_time = int(time.time())
    user_id, needs_refresh, new_token = SessionManager.verify_and_refresh_session(
        session_token, current_time
    )
    
    if not user_id:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    if needs_refresh and new_token:
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=SessionManager.SESSION_DURATION,
            secure=False,
            samesite="lax"
        )
        print(f"Session refreshed at {datetime.now()}")
    
    username = None
    user_info = None
    for uname, data in users_db.items():
        if data.get("user_id") == user_id:
            username = uname
            user_info = data
            break
    
    return {
        "user_id": user_id,
        "username": username,
        "name": user_info["name"] if user_info else "Unknown",
        "email": user_info["email"] if user_info else "unknown@example.com",
        "server_time": datetime.fromtimestamp(current_time).isoformat(),
        "session_refreshed": needs_refresh,
        "session_status": "valid"
    }

@router.get("/test-session", summary="Тестирование сессии")
async def test_session(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        return {"message": "No session token"}
    
    try:
        data = serializer.loads(token, max_age=None)
        parts = data.split('.')
        
        result = {
            "token_data": data,
            "current_time": datetime.now().isoformat(),
            "timestamp_parsed": None
        }
        
        if len(parts) == 2:
            user_id, timestamp = parts
            dt = datetime.fromtimestamp(int(timestamp))
            result["timestamp_parsed"] = dt.isoformat()
            result["user_id"] = user_id
            result["seconds_ago"] = int(time.time()) - int(timestamp)
            
        return result
    except Exception as e:
        return {"error": str(e), "token": token}