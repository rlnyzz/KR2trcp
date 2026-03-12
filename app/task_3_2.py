from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(tags=["3.2 - Работа с продуктами"])

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": 123,
                "name": "Smartphone",
                "category": "Electronics",
                "price": 599.99
            }
        }

products_db = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]

@router.get(
    "/product/{product_id}",
    response_model=Product,
    summary="Получить продукт по ID",
    description="Возвращает информацию о продукте по его уникальному идентификатору"
)
async def get_product(product_id: int):
    product = next((p for p in products_db if p["product_id"] == product_id), None)
    if not product:
        raise HTTPException(
            status_code=404, 
            detail=f"Product with id {product_id} not found"
        )
    return product

@router.get(
    "/products/search",
    response_model=List[Product],
    summary="Поиск продуктов",
    description="Поиск продуктов по ключевому слову с возможностью фильтрации по категории"
)
async def search_products(
    keyword: str = Query(
        ..., 
        description="Ключевое слово для поиска в названии продукта (обязательно)"
    ),
    category: Optional[str] = Query(
        None, 
        description="Категория для фильтрации результатов (опционально)"
    ),
    limit: int = Query(
        10, 
        ge=1, 
        le=100, 
        description="Максимальное количество возвращаемых продуктов (по умолчанию 10)"
    )
):
    results = []
    keyword_lower = keyword.lower()
    
    for product in products_db:
        if keyword_lower in product["name"].lower():
            if category:
                if product["category"].lower() == category.lower():
                    results.append(product)
            else:
                results.append(product)
    
    results = results[:limit]
    
    return results