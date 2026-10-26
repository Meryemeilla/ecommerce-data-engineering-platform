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
            INSERT INTO staging.order_items (
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price
            )
            SELECT
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price
            FROM raw.order_items
            ON CONFLICT (order_item_id) DO NOTHING;
        """)

        rows_inserted = cursor.rowcount

    connection.commit()
    print(
        f"Chargement terminé : "
        f"{rows_inserted} ligne(s) de commande insérée(s)."
    )

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()