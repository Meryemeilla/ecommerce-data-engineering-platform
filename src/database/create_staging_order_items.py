import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

try:
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS staging;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staging.order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price NUMERIC NOT NULL
            );
        """)

    connection.commit()
    print("Table staging.order_items créée avec succès !")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
