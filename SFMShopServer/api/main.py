from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Query

from SFMShopServer.database import queries
from SFMShopServer.database.connection import PostgresConnection
from SFMShopServer.models.order import OrderCreate
from SFMShopServer.models.product import ProductCreate
from SFMShopServer.models.user import UserCreate

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "database": "sfmshop",
    "user": "postgres",
    "password": "postgres"
}


@app.get("/products")
def get_products(limit: int = Query(10), offset: int = Query(0)):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            total, products = queries.get_all_products_query(conn, limit, offset)
            return {"total": total, "limit": limit, "offset": offset, "products": products}
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.get("/products/{product_id}")
def get_product(product_id: int):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            product = queries.get_product_by_id(conn, product_id)
            if not product:
                raise HTTPException(404, "Товар не найден")
            return product
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            new_product = queries.add_new_product(conn, product.name, product.price, product.quantity)
            return new_product
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductCreate):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            updated = queries.update_product(conn, product_id, product.name, product.price, product.quantity)
            if not updated:
                raise HTTPException(404, "Товар не найден")
            return updated
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            deleted = queries.delete_product(conn, product_id)
            if not deleted:
                raise HTTPException(404, "Товар не найден")
            return {"message": "Товар удалён"}
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.get("/users")
def get_users():
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            users = queries.get_all_users(conn)
            return users
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            user = queries.get_user(conn, user_id)
            if not user:
                raise HTTPException(404, "Пользователь не найден")
            return user
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.post("/users", status_code=201)
def create_user_endpoint(user: UserCreate):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            new_user = queries.create_new_user(conn, user.name, user.email)
            return new_user
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.get("/orders")
def get_orders():
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            orders = queries.get_all_orders(conn)
            return orders
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            result = queries.create_new_order(conn, order.user_id, order.items)
            if not result:
                raise HTTPException(500, "Ошибка при создании заказа")
            return {"id": result["id"], "user_id": order.user_id, "total": result["total"],
                    "created_at": datetime.now()}
    except ValueError as ve:
        raise HTTPException(404, str(ve))
    except Exception:
        raise HTTPException(500, "Ошибка сервера")


@app.get("/users/{user_id}/orders")
def get_user_orders(user_id: int):
    try:
        with PostgresConnection(**DB_CONFIG) as conn:
            user = queries.get_user(conn, user_id)
            if not user:
                raise HTTPException(404, "Пользователь не найден")
            orders = queries.get_user_order_history_query(conn, user_id)
            return orders
    except Exception:
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
