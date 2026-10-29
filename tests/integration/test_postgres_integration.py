import os

import psycopg2


def test_postgres_connection_and_temporary_table():
    connection = psycopg2.connect(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=os.getenv("TEST_DB_PORT", "5433"),
        database=os.getenv("TEST_DB_NAME", "ecommerce_test"),
        user=os.getenv("TEST_DB_USER", "ecommerce_user"),
        password=os.environ["TEST_DB_PASSWORD"],
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TEMPORARY TABLE integration_test (
                    id INTEGER PRIMARY KEY,
                    message TEXT NOT NULL
                )
            """)

            cursor.execute(
                "INSERT INTO integration_test (id, message) VALUES (%s, %s)",
                (1, "PostgreSQL integration test"),
            )

            cursor.execute(
                "SELECT message FROM integration_test WHERE id = %s",
                (1,),
            )

            result = cursor.fetchone()

        assert result == ("PostgreSQL integration test",)
    finally:
        connection.close()
