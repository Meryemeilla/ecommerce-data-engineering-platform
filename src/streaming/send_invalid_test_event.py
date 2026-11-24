
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

event = {
    "order_id": 9002,
    "customer_id": 43,
    "status": "unknown_status",
    "total_amount": -150
}

producer.send("orders", value=event)
producer.flush()
producer.close()

print("Événement invalide envoyé à Kafka.")
