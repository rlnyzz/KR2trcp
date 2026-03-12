from fastapi import APIRouter, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

router = APIRouter(tags=["3.1 - Модель пользователя"])

class UserCreate(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Имя пользователя (обязательно)"
    )
    email: EmailStr = Field(
        ..., 
        description="Email пользователя (обязателен, должен быть валидным)"
    )
    age: Optional[int] = Field(
        None, 
        ge=1, 
        le=150, 
        description="Возраст пользователя (опционально, положительное число)"
    )
    is_subscribed: Optional[bool] = Field(
        False, 
        description="Подписка на новости (опционально)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Alice",
                "email": "alice@example.com",
                "age": 30,
                "is_subscribed": True
            }
        }

@router.post(
    "/create_user", 
    response_model=UserCreate, 
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового пользователя",
    description="Принимает JSON с данными пользователя, валидирует и возвращает их"
)
async def create_user(user: UserCreate):
    return user