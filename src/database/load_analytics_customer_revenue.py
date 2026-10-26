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
            INSERT INTO analytics.customer_revenue (
                customer_id,
                first_name,
                last_name,
                delivered_revenue,
                delivered_orders
            )
            SELECT
                c.customer_id,
                c.first_name,
                c.last_name,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0)
                    AS delivered_revenue,
                COUNT(DISTINCT o.order_id)
                    AS delivered_orders
            FROM staging.customers c
            LEFT JOIN staging.orders o
                ON c.customer_id = o.customer_id
                AND o.status = 'delivered'
            LEFT JOIN staging.order_items oi
                ON o.order_id = oi.order_id
            GROUP BY
                c.customer_id,
                c.first_name,
                c.last_name
            ON CONFLICT (customer_id)
            DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                delivered_revenue = EXCLUDED.delivered_revenue,
                delivered_orders = EXCLUDED.delivered_orders;
        """)

        rows_processed = cursor.rowcount

    connection.commit()
    print(
        f"Analyse clients actualisée : "
        f"{rows_processed} client(s) traité(s)."
    )

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
