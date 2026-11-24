
import json
from kafka import KafkaProducer

def main():
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda value: json.dumps(value).encode("utf-8")
    )

    order_event = {
        "order_id": 9001,
        "customer_id": 42,
        "status": "delivered",
        "total_amount": 1250.75
    }

    try:
        future = producer.send("orders", value=order_event)
        metadata = future.get(timeout=10)

        print("Commande envoyée avec succès !")
        print("Topic :", metadata.topic)
        print("Partition :", metadata.partition)
        print("Offset :", metadata.offset)
        print("Événement :", order_event)

    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()
