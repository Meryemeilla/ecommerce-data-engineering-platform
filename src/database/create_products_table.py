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
    CREATE TABLE IF NOT EXISTS raw.products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        price NUMERIC(10, 2) CHECK (price >= 0),
        stock_quantity INTEGER CHECK (stock_quantity >= 0),
        created_at DATE
    );
""")


connection.commit()

cursor.close()
connection.close()

print("Table raw.products créée avec succès !")