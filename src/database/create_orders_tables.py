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
    CREATE TABLE IF NOT EXISTS raw.orders (
        order_id INTEGER PRIMARY KEY,

        customer_id INTEGER NOT NULL,

        order_date DATE NOT NULL,

        status VARCHAR(20) NOT NULL,

        CONSTRAINT fk_orders_customer
            FOREIGN KEY (customer_id)
            REFERENCES raw.customers(customer_id),

        CONSTRAINT check_order_status
            CHECK (
                status IN (
                    'pending',
                    'confirmed',
                    'shipped',
                    'delivered',
                    'cancelled'
                )
            )
    );
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw.order_items (
        order_item_id SERIAL PRIMARY KEY,

        order_id INTEGER NOT NULL,

        product_id INTEGER NOT NULL,

        quantity INTEGER NOT NULL,

        unit_price NUMERIC(10, 2) NOT NULL,

        CONSTRAINT fk_order_items_order
            FOREIGN KEY (order_id)
            REFERENCES raw.orders(order_id),

        CONSTRAINT fk_order_items_product
            FOREIGN KEY (product_id)
            REFERENCES raw.products(product_id),

        CONSTRAINT check_order_item_quantity
            CHECK (quantity > 0),

        CONSTRAINT check_order_item_unit_price
            CHECK (unit_price >= 0)
    );
""")


connection.commit()

cursor.close()
connection.close()

print("Tables raw.orders et raw.order_items créées avec succès !")