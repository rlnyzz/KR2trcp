from fastapi import APIRouter, Header, Response
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re

router = APIRouter(tags=["5.4 - Работа с заголовками"])

class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="user-agent")
    accept_language: str = Field(..., alias="accept-language")
    
    @validator('accept_language')
    def validate_accept_language(cls, v):
        if not v or not v.strip():
            raise ValueError('Accept-Language header cannot be empty')
        
        allowed_pattern = r'^[a-zA-Z0-9-,;.=q]+$'
        if not re.match(allowed_pattern, v):
            raise ValueError('Invalid Accept-Language format: contains invalid characters')
        
        parts = v.split(',')
        for part in parts:
            lang_part = part.split(';')[0].strip()
            if lang_part and not re.match(r'^[a-zA-Z]{2,3}(-[a-zA-Z]{2,3})?$', lang_part):
                pass
        
        return v
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "accept-language": "en-US,en;q=0.9,es;q=0.8"
            }
        }

@router.get(
    "/headers",
    summary="Получить заголовки запроса",
    description="Возвращает значения заголовков User-Agent и Accept-Language"
)
async def get_headers(headers: CommonHeaders = Header()):

    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@router.get(
    "/info",
    summary="Получить информацию с заголовками",
    description="Возвращает заголовки и добавляет X-Server-Time в ответ"
)
async def get_info(
    headers: CommonHeaders = Header(),
    response: Response = None
):
    server_time = datetime.now().isoformat()
    response.headers["X-Server-Time"] = server_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }

@router.get(
    "/headers/debug",
    summary="Отладка заголовков",
    description="Возвращает все заголовки запроса для отладки"
)
async def debug_headers(
    request: Request,
    user_agent: str = Header(None, alias="user-agent"),
    accept_language: str = Header(None, alias="accept-language")
):
    all_headers = dict(request.headers)
    return {
        "all_headers": all_headers,
        "extracted": {
            "user_agent": user_agent,
            "accept_language": accept_language
        }
    }