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
            CREATE TABLE IF NOT EXISTS staging.products (
                product_id INTEGER PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                price NUMERIC,
                stock_quantity INTEGER,
                created_at DATE
            );
        """)

    connection.commit()
    print("Table staging.products créée avec succès !")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()