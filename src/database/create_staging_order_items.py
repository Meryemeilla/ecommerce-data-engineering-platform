
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def main():
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
                CREATE SCHEMA IF NOT EXISTS staging;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staging.order_items (
                    order_item_id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price NUMERIC NOT NULL,
                    CONSTRAINT fk_order_items_orders
                        FOREIGN KEY (order_id)
                        REFERENCES staging.orders (order_id),
                    CONSTRAINT fk_order_items_products
                        FOREIGN KEY (product_id)
                        REFERENCES staging.products (product_id)
                );
            """)

            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'fk_order_items_orders'
                          AND conrelid = 'staging.order_items'::regclass
                    ) THEN
                        ALTER TABLE staging.order_items
                        ADD CONSTRAINT fk_order_items_orders
                        FOREIGN KEY (order_id)
                        REFERENCES staging.orders (order_id);
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'fk_order_items_products'
                          AND conrelid = 'staging.order_items'::regclass
                    ) THEN
                        ALTER TABLE staging.order_items
                        ADD CONSTRAINT fk_order_items_products
                        FOREIGN KEY (product_id)
                        REFERENCES staging.products (product_id);
                    END IF;
                END
                $$;
            """)

        connection.commit()
        print("Table staging.order_items et ses clés étrangères vérifiées.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
