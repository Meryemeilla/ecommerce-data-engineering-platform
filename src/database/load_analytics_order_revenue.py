
import os

import psycopg2
from dotenv import load_dotenv


def main():
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
                INSERT INTO analytics.order_revenue (
                    order_id,
                    order_date,
                    status,
                    order_total
                )
                SELECT
                    o.order_id,
                    o.order_date,
                    o.status,
                    COALESCE(
                        SUM(oi.quantity * oi.unit_price),
                        0
                    ) AS order_total
                FROM staging.orders o
                LEFT JOIN staging.order_items oi
                    ON o.order_id = oi.order_id
                GROUP BY
                    o.order_id,
                    o.order_date,
                    o.status
                ON CONFLICT (order_id)
                DO UPDATE SET
                    order_date = EXCLUDED.order_date,
                    status = EXCLUDED.status,
                    order_total = EXCLUDED.order_total;
            """)

            rows_processed = cursor.rowcount

        connection.commit()
        print(
            f"Table analytique mise a jour : "
            f"{rows_processed} commande(s) traitee(s)."
        )
    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
