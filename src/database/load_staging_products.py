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
            INSERT INTO staging.products (
                product_id,
                product_name,
                category,
                price,
                stock_quantity,
                created_at
            )
            SELECT
                product_id,
                TRIM(product_name),
                NULLIF(TRIM(category), ''),
                price,
                stock_quantity,
                created_at
            FROM raw.products
            ON CONFLICT (product_id) DO NOTHING;
        """)

        rows_inserted = cursor.rowcount

    connection.commit()

    print(
        f"Chargement terminé : "
        f"{rows_inserted} produit(s) inséré(s)."
    )

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()