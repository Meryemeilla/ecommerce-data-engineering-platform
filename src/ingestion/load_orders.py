import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()

CSV_PATH = "data/raw/orders.csv"


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def extract():
    print("1. Extraction des données...")

    df = pd.read_csv(
        CSV_PATH,
        dtype={
            "order_id": "string",
            "customer_id": "string",
        }
    )

    print(f"   {len(df)} lignes récupérées.")
    print()

    print(df)

    return df

def transform(df):
    print("2. Validation et transformation des données...")

    original_df = df.copy()

    # Nettoyage des chaînes de caractères
    df["status"] = df["status"].str.strip().str.lower()

    # Conversion de la date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Colonne qui contient les erreurs
    errors = pd.Series(
        "",
        index=df.index,
        dtype="string"
    )

    # 1. order_id obligatoire
    mask = (
        df["order_id"].isna()
        | (df["order_id"].str.strip() == "")
    )

    errors.loc[mask] += "missing_order_id;"

    # 2. customer_id obligatoire
    mask = (
        df["customer_id"].isna()
        | (df["customer_id"].str.strip() == "")
    )

    errors.loc[mask] += "missing_customer_id;"

    # 3. Date invalide
    mask = df["order_date"].isna()

    errors.loc[mask] += "invalid_order_date;"

    # 4. Status invalide
    allowed_statuses = {
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled",
    }

    mask = ~df["status"].isin(allowed_statuses)

    errors.loc[mask] += "invalid_status;"

    # 5. order_id dupliqué
    mask = df["order_id"].duplicated(keep=False)

    errors.loc[mask] += "duplicate_order_id;"

    # 6. Vérification de l'existence du client
    existing_customer_ids = get_existing_customer_ids()

    mask = (
        df["customer_id"].notna()
        & ~df["customer_id"].isin(existing_customer_ids)
    )

    errors.loc[mask] += "customer_not_found;"

    # Sauvegarde des erreurs
    df["rejection_reason"] = errors

    # Séparation valid / rejected
    rejected_mask = df["rejection_reason"] != ""

    rejected = original_df.loc[
        rejected_mask
    ].copy()

    rejected["rejection_reason"] = df.loc[
        rejected_mask,
        "rejection_reason"
    ].values

    valid = df.loc[
        ~rejected_mask
    ].copy()

    print()
    print("   DATA QUALITY REPORT")
    print("   -------------------")
    print(f"   Input rows:       {len(df)}")
    print(f"   Valid rows:       {len(valid)}")
    print(f"   Rejected rows:    {len(rejected)}")

    print()
    print(
        f"   Invalid date:     "
        f"{errors.str.contains('invalid_order_date').sum()}"
    )

    print(
        f"   Invalid status:   "
        f"{errors.str.contains('invalid_status').sum()}"
    )

    print(
        f"   Duplicate ID:     "
        f"{errors.str.contains('duplicate_order_id').sum()}"
    )

    return valid, rejected

def get_existing_customer_ids():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT customer_id
        FROM raw.customers;
    """)

    customer_ids = {
        str(row[0])
        for row in cursor.fetchall()
    }

    cursor.close()
    connection.close()

    return customer_ids

def load_valid(df):
    print()
    print("3. Chargement des commandes valides...")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.orders (
                order_id,
                customer_id,
                order_date,
                status
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING;
            """,
            (
                int(row["order_id"]),
                int(row["customer_id"]),
                row["order_date"],
                row["status"],
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} commandes valides traitées.")

def load_rejected(df):
    print("4. Chargement des commandes rejetées...")

    if df.empty:
        print("   Aucune commande rejetée.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    inserted_count = 0

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.rejected_orders (
                order_id,
                customer_id,
                order_date,
                status,
                rejection_reason
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (order_id, rejection_reason) DO NOTHING;
            """,
            (
                row["order_id"],
                row["customer_id"],
                row["order_date"],
                row["status"],
                row["rejection_reason"],
            ),
        )

        if cursor.rowcount == 1:
            inserted_count += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} commandes rejetées détectées.")
    print(f"   {inserted_count} nouveaux rejets enregistrés.")

if __name__ == "__main__":
    df = extract()

    valid, rejected = transform(df)

    print()
    print("VALID ORDERS")
    print(valid)

    print()
    print("REJECTED ORDERS")
    print(rejected)

    load_valid(valid)

    load_rejected(rejected)

    print()
    print("ETL Orders terminé !")