
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
            INSERT INTO staging.customers (
                customer_id,
                first_name,
                last_name,
                email,
                city,
                country,
                created_at
            )
            SELECT
                customer_id,
                NULLIF(TRIM(first_name), ''),
                NULLIF(TRIM(last_name), ''),
                NULLIF(LOWER(TRIM(email)), ''),
                NULLIF(TRIM(city), ''),
                NULLIF(TRIM(country), ''),
                created_at
            FROM raw.customers
            ON CONFLICT (customer_id) DO NOTHING;
        """)

        rows_inserted = cursor.rowcount

    connection.commit()
    print(f"Chargement terminé : {rows_inserted} client(s) inséré(s).")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
