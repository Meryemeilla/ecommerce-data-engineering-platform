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
            INSERT INTO staging.orders (
                order_id,
                customer_id,
                order_date,
                status
            )
            SELECT
                order_id,
                customer_id,
                order_date,
                LOWER(TRIM(status))
            FROM raw.orders
            ON CONFLICT (order_id) DO NOTHING;
        """)

        rows_inserted = cursor.rowcount

    connection.commit()
    print(
        f"Chargement terminé : "
        f"{rows_inserted} commande(s) insérée(s)."
    )

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
