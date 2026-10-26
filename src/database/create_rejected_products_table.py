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
    CREATE TABLE IF NOT EXISTS raw.rejected_products (
        rejection_id SERIAL PRIMARY KEY,
        product_id TEXT,
        product_name TEXT,
        category TEXT,
        price TEXT,
        stock_quantity TEXT,
        created_at TEXT,
        rejection_reason TEXT,
        rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT unique_product_rejection
        UNIQUE (product_id, rejection_reason)
    );
""")


connection.commit()

cursor.close()
connection.close()

print("Table raw.rejected_products créée avec succès !")