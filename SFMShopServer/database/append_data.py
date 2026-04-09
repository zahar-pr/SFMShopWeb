from datetime import datetime, timedelta
from decimal import Decimal

import psycopg2
import random
from psycopg2.extras import execute_batch

conn = psycopg2.connect(
    dbname="sfmshop",
    user="postgres",
    password="postgres",
    host="localhost",
)

orders = []

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 4, 9)

date_range_seconds = int((end_date - start_date).total_seconds())

for _ in range(1000):
    userid = random.randint(1, 1000)

    # сумма заказа от 500 до 100000
    total = round(random.uniform(500, 100000), 2)

    # случайная дата
    random_seconds = random.randint(0, date_range_seconds)
    createdat = start_date + timedelta(seconds=random_seconds)

    orders.append((
        userid,
        Decimal(str(total)),
        createdat
    ))

with conn:
    with conn.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO orders (userid, total, createdat)
            VALUES (%s, %s, %s)
            """,
            orders
        )

conn.close()

print("1000 заказов добавлено")