
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
    cursor = connection.cursor()

    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS staging;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging.customers (
            customer_id INTEGER PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            city VARCHAR(100),
            country VARCHAR(100),
            created_at DATE
        );
    """)

    connection.commit()

    cursor.close()
    print("Schéma staging et table staging.customers créés avec succès !")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
