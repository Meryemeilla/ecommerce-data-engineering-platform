import os
import time
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DoubleType
)
import logging
from pyspark.sql.functions import (
    col,
    from_json,
    when,
    trim,
    lower,
    lit,
    concat_ws
)
import psycopg2
from psycopg2.extras import execute_values
load_dotenv()
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/spark_streaming.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ecommerce_streaming")

def save_partition_to_postgres(rows):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cursor = connection.cursor()
        insert_query = """
            INSERT INTO streaming.orders_events (
                order_id,
                customer_id,
                status,
                total_amount,
                kafka_topic,
                kafka_partition,
                kafka_offset
            )
            VALUES %s
            ON CONFLICT (order_id)
            DO UPDATE SET
                customer_id = EXCLUDED.customer_id,
                status = EXCLUDED.status,
                total_amount = EXCLUDED.total_amount,
                kafka_topic = EXCLUDED.kafka_topic,
                kafka_partition = EXCLUDED.kafka_partition,
                kafka_offset = EXCLUDED.kafka_offset,
                processed_at = CURRENT_TIMESTAMP;
        """     
        values = [
            (
                row.order_id,
                row.customer_id,
                row.status,
                row.total_amount,
                row.kafka_topic,
                row.kafka_partition,
                row.kafka_offset
            )
            for row in rows
        ]


        if values:
            execute_values(cursor, insert_query, values)
            connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()



def save_rejected_partition(rows):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cursor = connection.cursor()

        insert_query = """
            INSERT INTO streaming.rejected_order_events (
                raw_event,
                rejection_reason,
                kafka_topic,
                kafka_partition,
                kafka_offset
            )
            VALUES %s
            ON CONFLICT (
                kafka_topic,
                kafka_partition,
                kafka_offset
            )
            WHERE kafka_topic IS NOT NULL
              AND kafka_partition IS NOT NULL
              AND kafka_offset IS NOT NULL
            DO NOTHING;
        """

        values = [
            (
                row.order_event,
                row.rejection_reason,
                row.kafka_topic,
                row.kafka_partition,
                row.kafka_offset
            )
            for row in rows
        ]

        if values:
            execute_values(cursor, insert_query, values)
            connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def save_valid_orders(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    start_time = time.perf_counter()

    row_count = batch_df.count()

    batch_df.foreachPartition(save_partition_to_postgres)

    duration = time.perf_counter() - start_time

    logger.info(
        "Batch %s | Commandes valides : %s | Durée : %.2f secondes",
        batch_id,
        row_count,
        duration
    )

def save_rejected_orders(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    start_time = time.perf_counter()

    row_count = batch_df.count()

    batch_df.foreachPartition(save_rejected_partition)

    duration = time.perf_counter() - start_time

    logger.info(
        "Batch %s | Événements rejetés : %s | Durée : %.2f secondes",
        batch_id,
        row_count,
        duration
    )


def main():
    spark = (
        SparkSession.builder
        .appName("EcommerceStructuredStreaming")
        .master("local[2]")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1,"
            "org.postgresql:postgresql:42.7.7"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    logger.info("Spark Structured Streaming démarré.")

    # Schéma des événements de commandes
    order_schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("customer_id", IntegerType(), True),
        StructField("status", StringType(), True),
        StructField("total_amount", DoubleType(), True)
    ])

    try:
        # Connexion au topic Kafka
        kafka_df = (
            spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "orders")
            .option("startingOffsets", "latest")
            .load()
        )

        # Conversion des messages Kafka en texte
        orders_json_df = kafka_df.select(
            col("value").cast("string").alias("order_event"),
            col("topic").alias("kafka_topic"),
            col("partition").alias("kafka_partition"),
            col("offset").alias("kafka_offset")
        )


        # Parsing du JSON en colonnes structurées 
        parsed_orders_df = orders_json_df.select(
            col("order_event"),
            col("kafka_topic"),
            col("kafka_partition"),
            col("kafka_offset"),
            from_json(col("order_event"), order_schema).alias("order")
        )


        # Extraction des colonnes
        orders_df = parsed_orders_df.select(
            col("order_event"),
            col("kafka_topic"),
            col("kafka_partition"),
            col("kafka_offset"),
            col("order.*")
        )


        # Normalisation du statut
        orders_df = orders_df.withColumn(
            "status",
            lower(trim(col("status")))
        )

        # Détection des erreurs de validation
        orders_df = orders_df.withColumn(
            "rejection_reason",
            concat_ws(
                "; ",
                when(col("order_id").isNull(), lit("order_id manquant ou invalide")),
                when(col("customer_id").isNull(), lit("customer_id manquant ou invalide")),
                when(
                    col("status").isNull() | (col("status") == ""),
                    lit("status manquant")
                ),
                when(
                    ~col("status").isin(
                        "pending",
                        "confirmed",
                        "shipped",
                        "delivered",
                        "cancelled"
                    ),
                    lit("status invalide")
                ),
                when(
                    col("total_amount").isNull(),
                    lit("total_amount manquant ou invalide")
                ),
                when(
                    col("total_amount") < 0,
                    lit("total_amount négatif")
                )
            )
        )

        # Séparer les événements valides et invalides
        valid_orders_df = orders_df.filter(
            col("rejection_reason") == ""
        )

        rejected_orders_df = orders_df.filter(
            col("rejection_reason") != ""
        )

        # Streaming des commandes valides
        valid_query = (
            valid_orders_df.writeStream
            .foreachBatch(save_valid_orders)
            .outputMode("append")
            .option(
                "checkpointLocation",
                "data/checkpoints/kafka_orders_valid"
            )
            .start()
        )

        # Streaming des commandes rejetées
        rejected_query = (
            rejected_orders_df.writeStream
            .foreachBatch(save_rejected_orders)
            .outputMode("append")
            .option(
                "checkpointLocation",
                "data/checkpoints/kafka_orders_rejected"
            )
            .start()
        )

        logger.info("Spark Structured Streaming est démarré.")
        logger.info("En attente de nouvelles commandes Kafka...")

        spark.streams.awaitAnyTermination()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
