

# Файл src/database/connection.py
import psycopg2
from psycopg2 import pool

# Параметры подключения
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sfmshop",
    "user": "postgres",
    "password": "postgres"
}

def get_connection():
    """Получить подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к БД: {e}")
        raise

def test_connection():
    """Проверить подключение к базе данных"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"Подключение успешно! Версия PostgreSQL: {version[0]}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_connection()




























