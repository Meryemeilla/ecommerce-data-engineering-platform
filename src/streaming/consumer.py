
import json
from kafka import KafkaConsumer
from kafka.serializer import Deserializer


class JsonDeserializer(Deserializer):

    def deserialize(self, topic, data):
        return json.loads(data.decode("utf-8"))


def create_consumer():
    return KafkaConsumer(
        "orders",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="ecommerce-orders-validation-v2",
        value_deserializer=JsonDeserializer()
    )


def main():
    consumer = create_consumer()
    message_count = 0
    expected_count = 5002

    print("Lecture des commandes Kafka...")

    try:
        for message in consumer:
            message_count += 1

            if message_count <= 3 or message_count == expected_count:
                print("Commande reçue :", message.value)

            if message_count >= expected_count:
                break

        print(f"\nNombre de commandes reçues : {message_count}")

    except KeyboardInterrupt:
        print("Arrêt du Consumer.")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()
