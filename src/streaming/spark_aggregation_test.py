from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, count

def main():
    spark = (
        SparkSession.builder
        .appName("EcommerceSparkAggregation")
        .master("local[2]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        data = [
            (1, "delivered", 450.50),
            (2, "pending", 200.00),
            (3, "delivered", 300.00),
            (4, "shipped", 150.00),
        ]

        columns = ["order_id", "status", "amount"]

        df = spark.createDataFrame(data, columns)

        result = (
            df.groupBy("status")
            .agg(
                count("order_id").alias("number_of_orders"),
                sum("amount").alias("total_amount")
            )
        )

        result.show()

    finally:
        spark.stop()

if __name__ == "__main__":
    main()