
from pyspark.sql import SparkSession

def main():
    spark = (
        SparkSession.builder
        .appName("EcommerceKafkaConnectionTest")
        .master("local[2]")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        print("Version Spark :", spark.version)

        kafka_df = (
            spark.read
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "orders")
            .option("startingOffsets", "earliest")
            .load()
        )

        print("Connexion Kafka réussie !")
        print("Nombre de partitions :", kafka_df.rdd.getNumPartitions())

        kafka_df.selectExpr(
            "CAST(key AS STRING)",
            "CAST(value AS STRING)",
            "topic",
            "partition",
            "offset"
        ).show(5, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
