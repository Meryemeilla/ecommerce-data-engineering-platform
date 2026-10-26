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


cursor = connection.cursor()


cursor.execute("""
    CREATE SCHEMA IF NOT EXISTS raw;
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw.rejected_order_items (
        rejection_id SERIAL PRIMARY KEY,

        order_item_id TEXT,
        order_id TEXT,
        product_id TEXT,
        quantity TEXT,
        unit_price TEXT,

        rejection_reason TEXT,

        rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT unique_order_item_rejection
        UNIQUE (order_item_id, rejection_reason)
    );
""")


connection.commit()

cursor.close()
connection.close()

print("Table raw.rejected_order_items créée avec succès !")