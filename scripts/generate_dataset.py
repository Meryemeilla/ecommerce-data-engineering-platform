import random
import pandas as pd
from datetime import date, timedelta


# Configuration générale
SEED = 42
random.seed(SEED)

START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)

OUTPUT_DIR = "data/generated"


def generate_customers(n=1000):
    """Generate synthetic e-commerce customers."""

    first_names = [
        "Ahmed", "Sara", "Youssef", "Meryeme", "Omar",
        "Salma", "Hamza", "Imane", "Anas", "Nour",
        "Karim", "Lina", "Adam", "Aya", "Mehdi",
        "Hajar", "Amine", "Sofia", "Rayan", "Khadija"
    ]

    last_names = [
        "Alaoui", "Amrani", "Bennani", "Idrissi",
        "Tazi", "Berrada", "Fassi", "El Mansouri",
        "Chraibi", "Lahlou", "Naciri", "Tahiri",
        "Filali", "Benjelloun", "Mansouri"
    ]

    cities = [
        "Casablanca", "Rabat", "Fes", "Marrakech",
        "Tangier", "Agadir", "Meknes", "Oujda",
        "Tetouan", "Kenitra"
    ]

    customers = []

    total_days = (END_DATE - START_DATE).days

    for customer_id in range(1, n + 1):

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        email = (
            f"{first_name.lower()}."
            f"{last_name.lower().replace(' ', '')}{customer_id}"
            "@example.com"
        )

        created_at = START_DATE + timedelta(
            days=random.randint(0, total_days)
        )

        customer = {
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "city": random.choice(cities),
            "country": "Morocco",
            "created_at": created_at.isoformat()
        }

        customers.append(customer)

    return pd.DataFrame(customers)


def generate_products(n=100):
    """Generate synthetic e-commerce products."""

    products_catalog = {
        "Electronics": [
            "Laptop", "Smartphone", "Wireless Mouse",
            "Mechanical Keyboard", "Monitor", "Headphones",
            "Tablet", "Smartwatch", "Webcam", "USB Hub"
        ],
        "Clothing": [
            "T-Shirt", "Jeans", "Jacket", "Sneakers",
            "Dress", "Hoodie", "Shirt", "Sweater"
        ],
        "Furniture": [
            "Office Chair", "Desk", "Bookshelf",
            "Coffee Table", "Sofa", "Bed Frame"
        ],
        "Home & Kitchen": [
            "Blender", "Coffee Maker", "Microwave",
            "Air Fryer", "Cookware Set", "Vacuum Cleaner"
        ],
        "Beauty": [
            "Face Cream", "Shampoo", "Perfume",
            "Sunscreen", "Hair Dryer"
        ],
        "Sports": [
            "Yoga Mat", "Dumbbells", "Running Shoes",
            "Football", "Bicycle", "Fitness Band"
        ]
    }

    products = []

    category_names = list(products_catalog.keys())
    total_days = (END_DATE - START_DATE).days

    for product_id in range(1, n + 1):

        category = random.choice(category_names)
        product_name = random.choice(
            products_catalog[category]
        )

        # Add an identifier to ensure unique product names
        product_name = f"{product_name} Model {product_id}"

        price = round(random.uniform(50, 15000), 2)

        stock_quantity = random.randint(0, 500)

        created_at = START_DATE + timedelta(
            days=random.randint(0, total_days)
        )

        products.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "price": price,
            "stock_quantity": stock_quantity,
            "created_at": created_at.isoformat()
        })

    return pd.DataFrame(products)


def generate_orders(customers_df, n=5000):
    """Generate synthetic e-commerce orders."""

    statuses = [
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled"
    ]

    orders = []

    for order_id in range(2001, 2001 + n):
        customer = customers_df.sample(
            n=1
        ).iloc[0]

        customer_created_at = date.fromisoformat(
            customer["created_at"]
        )

        order_date = customer_created_at + timedelta(
            days=random.randint(
                0,
                (END_DATE - customer_created_at).days
            )
        )

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date.isoformat(),
            "status": random.choice(statuses)
        })

    return pd.DataFrame(orders)



def generate_order_items(orders_df, products_df):
    """Generate synthetic order items."""

    order_items = []
    order_item_id = 20001

    for _, order in orders_df.iterrows():
        number_of_items = random.randint(3, 5)

        selected_products = products_df.sample(
            n=number_of_items
        )

        for _, product in selected_products.iterrows():
            order_items.append({
                "order_item_id": order_item_id,
                "order_id": int(order["order_id"]),
                "product_id": int(product["product_id"]),
                "quantity": random.randint(1, 5),
                "unit_price": float(product["price"])
            })

            order_item_id += 1

    return pd.DataFrame(order_items)



if __name__ == "__main__":
    customers_df = generate_customers(1000)
    customers_df.to_csv(
        f"{OUTPUT_DIR}/customers.csv",
        index=False
    )

    print("Customers generated successfully!")
    print(f"Total customers: {len(customers_df)}")

    products_df = generate_products(100)
    products_df.to_csv(
        f"{OUTPUT_DIR}/products.csv",
        index=False
    )

    print("\nProducts generated successfully!")
    print(f"Total products: {len(products_df)}")

    orders_df = generate_orders(customers_df, 5000)
    orders_df.to_csv(
        f"{OUTPUT_DIR}/orders.csv",
        index=False
    )

    print("\nOrders generated successfully!")
    print(f"Total orders: {len(orders_df)}")
    print(orders_df.head())


    order_items_df = generate_order_items(
        orders_df,
        products_df
    )

    order_items_df.to_csv(
        f"{OUTPUT_DIR}/order_items.csv",
        index=False
    )

    print("\nOrder items generated successfully!")
    print(f"Total order items: {len(order_items_df)}")
    print(order_items_df.head())


