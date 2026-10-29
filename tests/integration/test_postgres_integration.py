
import os

import psycopg2


def _connect_test_db():
    """Connecte uniquement à la base réservée aux tests."""
    connection = psycopg2.connect(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=os.getenv("TEST_DB_PORT", "5433"),
        database=os.getenv("TEST_DB_NAME", "ecommerce_test"),
        user=os.getenv("TEST_DB_USER", "ecommerce_user"),
        password=os.environ["TEST_DB_PASSWORD"],
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        database_name = cursor.fetchone()[0]

    assert database_name == os.getenv("TEST_DB_NAME", "ecommerce_test"), (
        f"Base inattendue : {database_name}"
    )

    return connection


def test_postgres_connection_and_temporary_table():
    connection = _connect_test_db()

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


def test_order_revenue_pipeline(monkeypatch):
    """Vérifie le calcul du chiffre d'affaires et les réexécutions."""

    # Récupère la configuration de la base de test.
    db_config = {
        "DB_HOST": os.getenv("TEST_DB_HOST", "localhost"),
        "DB_PORT": os.getenv("TEST_DB_PORT", "5433"),
        "DB_NAME": os.getenv("TEST_DB_NAME", "ecommerce_test"),
        "DB_USER": os.getenv("TEST_DB_USER", "ecommerce_user"),
        "DB_PASSWORD": os.environ["TEST_DB_PASSWORD"],
    }

    # Force le script testé à utiliser la base de test.
    for key, value in db_config.items():
        monkeypatch.setenv(key, value)

    from src.database.load_analytics_order_revenue import main

    order_id = 987654321
    item_id_1 = 987654321
    item_id_2 = 987654322

    connection = _connect_test_db()

    try:
        with connection.cursor() as cursor:
            # Prépare les tables nécessaires dans la base de test.
            cursor.execute("""
                CREATE SCHEMA IF NOT EXISTS staging;
                CREATE SCHEMA IF NOT EXISTS analytics;

                CREATE TABLE IF NOT EXISTS staging.orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    order_date DATE NOT NULL,
                    status VARCHAR(50) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS staging.order_items (
                    order_item_id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price NUMERIC NOT NULL
                );

                CREATE TABLE IF NOT EXISTS analytics.order_revenue (
                    order_id INTEGER PRIMARY KEY,
                    order_date DATE NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    order_total NUMERIC NOT NULL
                );
            """)

            # Nettoie une éventuelle exécution précédente du test.
            cursor.execute(
                "DELETE FROM analytics.order_revenue WHERE order_id = %s",
                (order_id,),
            )
            cursor.execute(
                "DELETE FROM staging.order_items WHERE order_id = %s",
                (order_id,),
            )
            cursor.execute(
                "DELETE FROM staging.orders WHERE order_id = %s",
                (order_id,),
            )

            # Crée une commande de test : 2 × 150 + 1 × 50 = 350.
            cursor.execute(
                """
                INSERT INTO staging.orders
                    (order_id, customer_id, order_date, status)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, 1, "2026-01-15", "delivered"),
            )

            cursor.executemany(
                """
                INSERT INTO staging.order_items
                    (order_item_id, order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (item_id_1, order_id, 1, 2, 150),
                    (item_id_2, order_id, 2, 1, 50),
                ],
            )

        connection.commit()

        # Première exécution du vrai script.
        main()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT order_total
                FROM analytics.order_revenue
                WHERE order_id = %s
                """,
                (order_id,),
            )
            result = cursor.fetchone()

        assert result is not None
        assert float(result[0]) == 350.0

        # Deuxième exécution : aucune ligne en double ne doit apparaître.
        main()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*), MAX(order_total)
                FROM analytics.order_revenue
                WHERE order_id = %s
                """,
                (order_id,),
            )
            count, total = cursor.fetchone()

        assert count == 1
        assert float(total) == 350.0

    finally:
        # Nettoyage des seules données créées par ce test.
        connection.rollback()

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM analytics.order_revenue WHERE order_id = %s",
                (order_id,),
            )
            cursor.execute(
                "DELETE FROM staging.order_items WHERE order_id = %s",
                (order_id,),
            )
            cursor.execute(
                "DELETE FROM staging.orders WHERE order_id = %s",
                (order_id,),
            )

        connection.commit()
        connection.close()
