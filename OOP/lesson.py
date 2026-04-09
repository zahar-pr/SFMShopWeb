import time

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "sfmshop",
    "user": "postgres",
    "password": "postgres",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def measure_index_performance():
    with get_connection() as connect:
        with connect.cursor() as cursor:
            print("Тест 1: Поиск товара по названию")

            start_time = time.time()
            cursor.execute("SELECT * FROM products WHERE name = %s", ("Ноутбук",))
            result = cursor.fetchone()
            time_without_index = time.time() - start_time

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
            connect.commit()

            start_time = time.time()
            cursor.execute("SELECT * FROM products WHERE name = %s", ("Ноутбук",))
            result = cursor.fetchone()
            time_with_index = time.time() - start_time

            print(f"  Без индекса: {time_without_index:.6f} сек")
            print(f"  С индексом: {time_with_index:.6f} сек")
            if time_with_index > 0:
                speedup = time_without_index / time_with_index
                print(f"  Ускорение: {speedup:.2f}x")

            print("\nТест 2: Поиск заказов по пользователю")

            # Без индекса
            cursor.execute("SELECT * FROM orders WHERE user_id = %s", (1,))
            results = cursor.fetchall()
            time_without_index = time.time() - start_time

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
            connect.commit()

            start_time = time.time()
            cursor.execute("SELECT * FROM orders WHERE user_id = %s", (1,))
            results = cursor.fetchall()
            time_with_index = time.time() - start_time

            print(f"  Без индекса: {time_without_index:.6f} сек")
            print(f"  С индексом: {time_with_index:.6f} сек")
            if time_with_index > 0:
                speedup = time_without_index / time_with_index
                print(f"  Ускорение: {speedup:.2f}x")


if __name__ == "__main__":
    measure_index_performance()