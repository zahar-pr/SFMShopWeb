from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Query

from SFMShopServer.database import queries
from SFMShopServer.database.connection import PostgresConnection
from SFMShopServer.models.order import OrderCreate
from SFMShopServer.models.product import ProductCreate
from SFMShopServer.models.user import UserCreate

app = FastAPI()
cache_service = CacheService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DB_CONFIG = {
    "host": "localhost",
    "database": "sfmshop",
    "user": "postgres",
    "password": "postgres"
}



from datetime import datetime
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends

from SFMShopServer.cache_service import CacheService
from SFMShopServer.log_service import LogService
from SFMShopServer.database.connection import AsyncSessionLocal
from SFMShopServer.database import queries
from SFMShopServer.models.product import ProductCreate
from SFMShopServer.models.user import UserCreate
from SFMShopServer.models.order import OrderCreate

app = FastAPI()
cache_service = CacheService()
log_service = LogService()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/products")
async def get_products(limit: int = Query(10), offset: int = Query(0), db=Depends(get_db)):
    try:
        # проверяем кэш
        cached = await cache_service.get_products("products_list")
        if cached:
            await log_service.log_access("anonymous", "/products", "GET")
            return {"source": "cache", "products": cached}

        # если нет в кэше, идем в БД
        total, products = await queries.get_all_products(db, limit, offset)
        products_dict = [p.__dict__ for p in products]

        # сохраняем в кэш
        await cache_service.set_products("products_list", products_dict, ttl=300)
        await log_service.log_access("anonymous", "/products", "GET")
        return {"source": "db", "products": products_dict, "total": total}

    except Exception as e:
        await log_service.log_error(str(e), repr(e))
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.get("/products/{product_id}")
async def get_product(product_id: int, db=Depends(get_db)):
    try:
        product = await queries.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(404, "Товар не найден")
        await log_service.log_access("anonymous", f"/products/{product_id}", "GET")
        return product
    except Exception as e:
        await log_service.log_error(str(e), repr(e))
        raise HTTPException(500, "Ошибка сервера")


@app.post("/products", status_code=201)
async def create_product(product: ProductCreate, db=Depends(get_db)):
    try:
        new_product = await queries.add_new_product(db, product.name, product.price, product.quantity)
        # инвалидируем кэш
        await cache_service.invalidate("products_list")
        await log_service.log_access("anonymous", "/products", "POST")
        return new_product
    except Exception as e:
        await log_service.log_error(str(e), repr(e))
        raise HTTPException(500, "Ошибка сервера")


@app.get("/users")
async def get_users(db=Depends(get_db)):
    try:
        users = await queries.get_all_users(db)
        await log_service.log_access("anonymous", "/users", "GET")
        return users
    except Exception as e:
        await log_service.log_error(str(e), repr(e))
        raise HTTPException(500, "Ошибка сервера")


@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate, db=Depends(get_db)):
    try:
        result = await queries.create_new_order(db, order.user_id, order.items)
        if not result:
            raise HTTPException(500, "Ошибка при создании заказа")
        await log_service.log_access("anonymous", "/orders", "POST")
        return {"id": result["id"], "user_id": order.user_id, "total": result["total"], "created_at": datetime.now()}
    except ValueError as ve:
        await log_service.log_error(str(ve), repr(ve))
        raise HTTPException(404, str(ve))
    except Exception as e:
        await log_service.log_error(str(e), repr(e))
        raise HTTPException(500, "Ошибка сервера")



def test_api():
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Тест GET /products
    response = client.get("/products")
    assert response.status_code == 200
    print("GET /products: OK")

    # Тест GET /products/{id}
    response = client.get("/products/1")
    assert response.status_code == 200
    print("GET /products/1: OK")

    # Тест POST /orders
    response = client.post("/orders", json={"user_id": 1, "product_id": 2, "quantity": 1})
    assert response.status_code == 201
    print("POST /orders: OK")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    test_api()
