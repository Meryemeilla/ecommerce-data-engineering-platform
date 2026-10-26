import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()

CSV_PATH = "data/raw/order_items.csv"


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
            "order_item_id": "string",
            "order_id": "string",
            "product_id": "string",
        }
    )

    print(f"   {len(df)} lignes récupérées.")
    print()

    print(df)

    return df

def get_existing_order_ids():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT order_id
        FROM raw.orders;
    """)

    order_ids = {
        str(row[0])
        for row in cursor.fetchall()
    }

    cursor.close()
    connection.close()

    return order_ids

def get_existing_product_ids():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id
        FROM raw.products;
    """)

    product_ids = {
        str(row[0])
        for row in cursor.fetchall()
    }

    cursor.close()
    connection.close()

    return product_ids
def transform(df):
    print("2. Validation et transformation des données...")

    original_df = df.copy()

    df["source_row_number"] = df.index + 2
    original_df["source_row_number"] = df["source_row_number"]

    # Conversion des valeurs numériques
    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    # Colonne des erreurs
    errors = pd.Series(
        "",
        index=df.index,
        dtype="string"
    )

    # 1. order_item_id obligatoire
    mask = (
        df["order_item_id"].isna()
        | (df["order_item_id"].str.strip() == "")
    )

    errors.loc[mask] += "missing_order_item_id;"

    # 2. order_id obligatoire
    mask = (
        df["order_id"].isna()
        | (df["order_id"].str.strip() == "")
    )

    errors.loc[mask] += "missing_order_id;"

    # 3. product_id obligatoire
    mask = (
        df["product_id"].isna()
        | (df["product_id"].str.strip() == "")
    )

    errors.loc[mask] += "missing_product_id;"

    # 4. Quantité invalide
    mask = (
        df["quantity"].isna()
        | (df["quantity"] <= 0)
    )

    errors.loc[mask] += "invalid_quantity;"

    # 5. Prix invalide
    mask = (
        df["unit_price"].isna()
        | (df["unit_price"] < 0)
    )

    errors.loc[mask] += "invalid_unit_price;"

    # 6. order_item_id dupliqué
    mask = df["order_item_id"].duplicated(keep=False)

    errors.loc[mask] += "duplicate_order_item_id;"

    # 7. Vérification de l'existence des commandes
    existing_order_ids = get_existing_order_ids()

    mask = (
        df["order_id"].notna()
        & ~df["order_id"].isin(existing_order_ids)
    )

    errors.loc[mask] += "order_not_found;"

    # 8. Vérification de l'existence des produits
    existing_product_ids = get_existing_product_ids()

    mask = (
        df["product_id"].notna()
        & ~df["product_id"].isin(existing_product_ids)
    )

    errors.loc[mask] += "product_not_found;"

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
        f"   Invalid quantity: "
        f"{errors.str.contains('invalid_quantity').sum()}"
    )

    print(
        f"   Invalid unit price: "
        f"{errors.str.contains('invalid_unit_price').sum()}"
    )

    print(
        f"   Duplicate item ID: "
        f"{errors.str.contains('duplicate_order_item_id').sum()}"
    )

    print(
        f"   Order not found: "
        f"{errors.str.contains('order_not_found').sum()}"
    )

    print(
        f"   Product not found: "
        f"{errors.str.contains('product_not_found').sum()}"
    )

    return valid, rejected

def load_valid(df):
    print()
    print("3. Chargement des lignes valides...")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.order_items (
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (order_item_id) DO NOTHING;
            """,
            (
                int(row["order_item_id"]),
                int(row["order_id"]),
                int(row["product_id"]),
                int(row["quantity"]),
                row["unit_price"],
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} lignes valides traitées.")

def load_rejected(df):
    print("4. Chargement des lignes rejetées...")

    if df.empty:
        print("   Aucune donnée rejetée.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    inserted_count = 0

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.rejected_order_items (
                source_row_number,
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                rejection_reason
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_row_number, rejection_reason) DO NOTHING;
            """,
            (
                int(row["source_row_number"]),
                row["order_item_id"],
                row["order_id"],
                row["product_id"],
                row["quantity"],
                row["unit_price"],
                row["rejection_reason"],
            ),
        )

        if cursor.rowcount == 1:
            inserted_count += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} lignes rejetées détectées.")
    print(f"   {inserted_count} nouveaux rejets enregistrés.")

if __name__ == "__main__":
    df = extract()

    valid, rejected = transform(df)

    load_valid(valid)

    load_rejected(rejected)

    print()
    print("ETL Order Items terminé !")