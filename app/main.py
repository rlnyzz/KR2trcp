from fastapi import FastAPI
from task_3_1 import router as router_3_1
from task_3_2 import router as router_3_2
from task_5_1 import router as router_5_1
from task_5_2 import router as router_5_2
from task_5_3 import router as router_5_3
from task_5_4 import router as router_5_4

app = FastAPI(
    title="Контрольная работа №2",
    description="Технологии разработки серверных приложений",
    version="1.0.0"
)

app.include_router(router_3_1)
app.include_router(router_3_2)
app.include_router(router_5_1)
app.include_router(router_5_2)
app.include_router(router_5_3)
app.include_router(router_5_4)

@app.get("/")
async def root():
    """Корневой маршрут с информацией о доступных endpoint'ах"""
    return {
        "message": "Контрольная работа №2",
        "available_endpoints": {
            "task_3.1": {
                "POST /create_user": "Создание пользователя"
            },
            "task_3.2": {
                "GET /product/{product_id}": "Получение продукта",
                "GET /products/search": "Поиск продуктов"
            },
            "task_5.1": {
                "POST /login": "Простая аутентификация",
                "GET /user": "Защищенный профиль"
            },
            "task_5.2": {
                "POST /login/v2": "Аутентификация с подписью",
                "GET /profile": "Профиль с проверкой подписи"
            },
            "task_5.3": {
                "POST /login/v3": "Аутентификация с динамической сессией",
                "GET /profile/v3": "Профиль с динамическим продлением"
            },
            "task_5.4": {
                "GET /headers": "Получение заголовков",
                "GET /info": "Информация с заголовками"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)