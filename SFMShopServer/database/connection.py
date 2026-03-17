import psycopg2
from psycopg2 import Error


class PostgresConnection:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            return self.conn
        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()

        self.conn.close()


def create_user(conn, name, email):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                   INSERT INTO users (name, email)
                   VALUES (%s, %s)
                   RETURNING id
               """, (name, email))

            user_id = cursor.fetchone()[0]
            return user_id
    except Error as e:
        print(f"Ошибка при создании пользователя: {e}")
        return None


def add_product(conn, name, price, quantity):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)
            """, (name, price, quantity,))
        print(f"Товар добавлен: {name}, {price}, {quantity}")
    except Error as e:
        print(f"Ошибка при добавлении товара: {e}")
        return None


def get_all_products(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
        return products
    except Error as e:
        print(f"Ошибка при получении товаров: {e}")
        return None


def update_product_price(conn, product_id, new_price):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE products SET price = %s WHERE id = %s
            """, (new_price, product_id,))
        print(f"Цена обновлена: {new_price}")
    except Error as e:
        print(f"Ошибка при обновлении цены товара: {e}")
        return None


def get_user_by_id(conn, user_id) -> dict | None:
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM users
                WHERE id = %s
            """, (user_id,))
            result = cursor.fetchone()
            return result if result else None
    except Error as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None


def delete_order(conn, order_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM orders
                WHERE id = %s
            """, (order_id,))
            count_delete_string = cursor.rowcount()
            return count_delete_string if count_delete_string != [] else ValueError(
                f"Заказ с id = {order_id} не найден")
    except Error as e:
        print(f"Ошибка при удалении заказа: {e}")
        return None


def main():
    pass


if __name__ == "__main__":
    main()
