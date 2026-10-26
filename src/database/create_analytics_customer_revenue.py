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
            CREATE TABLE IF NOT EXISTS analytics.customer_revenue (
                customer_id INTEGER PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                delivered_revenue NUMERIC NOT NULL,
                delivered_orders INTEGER NOT NULL
            );
        """)

    connection.commit()
    print("Table analytics.customer_revenue créée avec succès !")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
