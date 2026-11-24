import csv
import json
from pathlib import Path
from decimal import Decimal
from kafka import KafkaProducer


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def create_producer():
    return KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=json_serializer
    )

def calculate_order_totals():
    order_totals = {}

    csv_path = Path("data/generated/order_items.csv")

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            order_id = int(row["order_id"])
            quantity = int(row["quantity"])
            unit_price = Decimal(row["unit_price"])

            line_total = quantity * unit_price

            order_totals[order_id] = (
                order_totals.get(order_id, Decimal("0.00"))
                + line_total
            )

    return order_totals


def check_orders_without_items():
    order_totals = calculate_order_totals()

    csv_path = Path("data/generated/orders.csv")

    orders_without_items = []

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            order_id = int(row["order_id"])

            if order_id not in order_totals:
                orders_without_items.append(order_id)

    print("Commandes sans articles :", len(orders_without_items))
    print("Identifiants :", orders_without_items[:10])

def main():
    producer = create_producer()
    order_totals = calculate_order_totals()

    csv_path = Path("data/generated/orders.csv")

    try:
        with csv_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                order_id = int(row["order_id"])
                total_amount = order_totals.get(
                    order_id,
                    Decimal("0.00")
                )

                order = {
                    "order_id": order_id,
                    "customer_id": int(row["customer_id"]),
                    "status": row["status"],
                    "total_amount": float(total_amount)
                }

                producer.send("orders", value=order)
                print("Commande envoyée :", order)

        producer.flush()
        print("Toutes les commandes ont été envoyées.")

    except Exception as error:
        print("Erreur lors de l'envoi :", error)

    finally:
        producer.close()


if __name__ == "__main__":
    main()
