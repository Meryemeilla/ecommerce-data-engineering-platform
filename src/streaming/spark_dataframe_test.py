
import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession


def main():
    spark = (
        SparkSession.builder
        .appName("EcommerceDataFrameTest")
        .master("local[1]")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.python.worker.faulthandler.enabled", "true")
        .getOrCreate()
    )

    try:
        data = [
            (1, "delivered", 450.50),
            (2, "pending", 200.00),
            (3, "shipped", 300.00),
        ]

        columns = ["order_id", "status", "amount"]
        df = spark.createDataFrame(data, columns)

        df.show()
        print("Nombre de commandes :", df.count())

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
