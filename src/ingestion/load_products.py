import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()

CSV_PATH = "data/raw/products.csv"


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
        dtype={"product_id": "string"}
    )

    print(f"   {len(df)} lignes récupérées.")

    return df


def transform(df):
    print("2. Validation et transformation des données...")

    original_df = df.copy()

    # Nettoyage des chaînes
    for column in ["product_name", "category"]:
        df[column] = df[column].str.strip()

    # Conversion du prix
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    # Conversion du stock
    df["stock_quantity"] = pd.to_numeric(
        df["stock_quantity"],
        errors="coerce"
    )

    # Conversion de la date
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    errors = pd.Series("", index=df.index, dtype="string")

    # Product ID obligatoire
    mask = (
        df["product_id"].isna()
        | (df["product_id"].str.strip() == "")
    )

    errors.loc[mask] += "missing_product_id;"

    # Nom obligatoire
    mask = (
        df["product_name"].isna()
        | (df["product_name"] == "")
    )

    errors.loc[mask] += "missing_product_name;"

    # Prix négatif
    mask = df["price"] < 0

    errors.loc[mask] += "negative_price;"

    # Stock négatif
    mask = df["stock_quantity"] < 0

    errors.loc[mask] += "negative_stock;"

    # Date invalide
    mask = df["created_at"].isna()

    errors.loc[mask] += "invalid_created_at;"

    # Product ID dupliqué
    mask = df["product_id"].duplicated(keep=False)

    errors.loc[mask] += "duplicate_product_id;"

    df["rejection_reason"] = errors

    rejected_mask = df["rejection_reason"] != ""

    rejected = original_df.loc[rejected_mask].copy()

    rejected["rejection_reason"] = df.loc[
        rejected_mask,
        "rejection_reason"
    ].values

    valid = df.loc[~rejected_mask].copy()

    print()
    print("   DATA QUALITY REPORT")
    print("   -------------------")
    print(f"   Input rows:       {len(df)}")
    print(f"   Valid rows:       {len(valid)}")
    print(f"   Rejected rows:    {len(rejected)}")

    return valid, rejected


def load_valid(df):
    print()
    print("3. Chargement des données valides...")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.products (
                product_id,
                product_name,
                category,
                price,
                stock_quantity,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING;
            """,
            (
                int(row["product_id"]),
                row["product_name"],
                row["category"],
                row["price"],
                int(row["stock_quantity"]),
                row["created_at"],
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} lignes valides traitées.")


def load_rejected(df):
    print("4. Chargement des données rejetées...")

    if df.empty:
        print("   Aucune donnée rejetée.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    inserted_count = 0

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.rejected_products (
                product_id,
                product_name,
                category,
                price,
                stock_quantity,
                created_at,
                rejection_reason
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id, rejection_reason) DO NOTHING;
            """,
            (
                row["product_id"],
                row["product_name"],
                row["category"],
                row["price"],
                row["stock_quantity"],
                row["created_at"],
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


def main():
    df = extract()

    valid, rejected = transform(df)

    load_valid(valid)

    load_rejected(rejected)

    print()
    print("ETL Products terminé !")


if __name__ == "__main__":
    main()