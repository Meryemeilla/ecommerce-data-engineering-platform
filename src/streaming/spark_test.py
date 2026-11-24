import os
import sys

# Forcer l'utilisation du Python de l'environnement virtuel
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession


def main():
    print("Python utilisé :", sys.executable)

    spark = (
        SparkSession.builder
        .appName("EcommercePythonWorkerTest")
        .master("local[1]")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .config("spark.python.worker.faulthandler.enabled", "true")
        .getOrCreate()
    )

    try:
        print("Spark version :", spark.version)

        df = spark.range(1, 4)
        result = df.rdd.map(lambda row: row.id * 2).collect()

        print("Résultat du Python Worker :", result)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()