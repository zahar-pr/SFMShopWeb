from datetime import datetime

from psycopg2 import Error
from psycopg2.extras import RealDictCursor


def get_all_products_query(conn, limit=10, offset=0):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
        products = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS total FROM products")
        total = cur.fetchone()["total"]
        return total, products
    except Error as e:
        print(f"Ошибка при получении продуктов: {e}")
        return 0, []


def get_product_by_id(conn, product_id):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        return cur.fetchone()
    except Error as e:
        print(f"Ошибка при получении продукта: {e}")
        return None


def add_new_product(conn, name, price, quantity):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s) RETURNING *",
            (name, price, quantity)
        )
        return cur.fetchone()
    except Error as e:
        print(f"Ошибка при добавлении продукта: {e}")
        return None


def update_product(conn, product_id, name, price, quantity):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "UPDATE products SET name=%s, price=%s, quantity=%s WHERE id=%s RETURNING *",
            (name, price, quantity, product_id)
        )
        return cur.fetchone()
    except Error as e:
        print(f"Ошибка при обновлении продукта: {e}")
        return None


def delete_product(conn, product_id):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("DELETE FROM products WHERE id=%s RETURNING id", (product_id,))
        return cur.fetchone()
    except Error as e:
        print(f"Ошибка при удалении продукта: {e}")
        return None


def get_all_users(conn):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users ORDER BY id")
        return cur.fetchall()
    except Error as e:
        print(f"Ошибка при получении пользователей: {e}")
        return []


def get_user(conn, user_id):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return cur.fetchone()
    except Error as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None


def create_new_user(conn, name, email):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING *",
            (name, email)
        )
        return cur.fetchone()
    except Error as e:
        print(f"Ошибка при создании пользователя: {e}")
        return None


def get_all_orders(conn):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM orders ORDER BY createdat DESC")
        return cur.fetchall()
    except Error as e:
        print(f"Ошибка при получении заказов: {e}")
        return []


def create_new_order(conn, user_id, items):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "INSERT INTO orders (userid, total, createdat) VALUES (%s, %s, %s) RETURNING id",
            (user_id, 0, datetime.now())
        )
        order_id = cur.fetchone()["id"]
        total = 0
        for item in items:
            cur.execute("SELECT * FROM products WHERE id=%s", (item["product_id"],))
            product = cur.fetchone()
            if not product:
                raise ValueError(f"Товар {item['product_id']} не найден")
            total += product["price"] * item["quantity"]
            cur.execute(
                "INSERT INTO order_items (orderid, productid, quantity) VALUES (%s,%s,%s)",
                (order_id, item["product_id"], item["quantity"])
            )
        cur.execute("UPDATE orders SET total=%s WHERE id=%s", (total, order_id))
        return {"id": order_id, "total": total}
    except Error as e:
        print(f"Ошибка при создании заказа: {e}")
        return None


def get_user_order_history_query(conn, user_id):
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                users.name AS user_name, 
                products.name AS product_name, 
                products.price AS price_per_unit,
                order_items.quantity AS quantity,
                products.price * order_items.quantity AS total_sum
            FROM users
            INNER JOIN orders ON orders.userid = users.id
            INNER JOIN order_items ON order_items.orderid = orders.id
            INNER JOIN products ON order_items.productid = products.id
            WHERE users.id = %s
            ORDER BY orders.createdat ASC
        """, (user_id,))
        return cur.fetchall()
    except Error as e:
        print(f"Ошибка при получении истории заказов пользователя: {e}")
        return []
