
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


CHECKS = {
    "Clients sans email": """
        SELECT COUNT(*)
        FROM staging.customers
        WHERE email IS NULL OR TRIM(email) = '';
    """,
    "Clients sans prénom": """
        SELECT COUNT(*)
        FROM staging.customers
        WHERE first_name IS NULL OR TRIM(first_name) = '';
    """,
    "Produits sans nom": """
        SELECT COUNT(*)
        FROM staging.products
        WHERE product_name IS NULL OR TRIM(product_name) = '';
    """,
    "Produits avec prix négatif": """
        SELECT COUNT(*)
        FROM staging.products
        WHERE price < 0;
    """,
    "Produits avec stock négatif": """
        SELECT COUNT(*)
        FROM staging.products
        WHERE stock_quantity < 0;
    """,
    
    "Commandes sans client valide": """
        SELECT COUNT(*)
        FROM staging.orders o
        LEFT JOIN staging.customers c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL;
    """,
    "Commandes avec statut invalide": """
        SELECT COUNT(*)
        FROM staging.orders
        WHERE status NOT IN (
            'pending', 'confirmed', 'shipped',
            'delivered', 'cancelled'
        ) OR status IS NULL OR TRIM(status) = '';
    """,
    "Lignes de commande sans commande valide": """
        SELECT COUNT(*)
        FROM staging.order_items oi
        LEFT JOIN staging.orders o
            ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL;
    """,
    "Lignes de commande sans produit valide": """
        SELECT COUNT(*)
        FROM staging.order_items oi
        LEFT JOIN staging.products p
            ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL;
    """,
    "Lignes avec quantité invalide": """
        SELECT COUNT(*)
        FROM staging.order_items
        WHERE quantity <= 0;
    """,
    "Lignes avec prix unitaire négatif": """
        SELECT COUNT(*)
        FROM staging.order_items
        WHERE unit_price < 0;
    """,

}




def main():
    total_anomalies = 0
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            print("\n===== RAPPORT DE QUALITÉ DES DONNÉES =====\n")

            for check_name, query in CHECKS.items():
                cursor.execute(query)
                invalid_rows = cursor.fetchone()[0]
                total_anomalies += invalid_rows

                status = "OK" if invalid_rows == 0 else "À CORRIGER"

                print(
                    f"{check_name}: {invalid_rows} anomalie(s) | {status}"
                )

            print("\n===== FIN DU RAPPORT =====")
            print(f"Total des anomalies : {total_anomalies}")

            if total_anomalies > 0:
                print("ÉCHEC : le contrôle qualité a détecté des anomalies.")
                sys.exit(1)

            print("SUCCÈS : toutes les règles de qualité sont respectées.")

    except psycopg2.Error as error:
        print(f"ERREUR BASE DE DONNÉES : {error}", file=sys.stderr)
        sys.exit(1)

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
