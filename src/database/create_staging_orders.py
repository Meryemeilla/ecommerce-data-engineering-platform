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
            CREATE TABLE IF NOT EXISTS staging.orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                status VARCHAR(50) NOT NULL
            );
        """)

    connection.commit()
    print("Table staging.orders créée avec succès !")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
