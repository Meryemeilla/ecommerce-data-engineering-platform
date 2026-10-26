import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()

CSV_PATH = "data/raw/customers.csv"


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
        dtype={"customer_id": "string"}
    )

    print(f"   {len(df)} lignes récupérées.")

    return df


def transform(df):
    print("2. Validation et transformation des données...")

    # Garder une copie des données originales
    original_df = df.copy()

    # Nettoyage des espaces
    for column in ["first_name", "last_name", "email", "city", "country"]:
        df[column] = df[column].str.strip()

    # Nettoyage de l'email
    df["email"] = df["email"].str.lower()

    # Conversion de la date
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    # Liste des problèmes par ligne
    errors = pd.Series("", index=df.index, dtype="string")

    # 1. Customer ID manquant
    mask = df["customer_id"].isna() | (df["customer_id"].str.strip() == "")
    errors.loc[mask] = errors.loc[mask] + "missing_customer_id;"

    # 2. Email manquant
    mask = df["email"].isna() | (df["email"] == "")
    errors.loc[mask] = errors.loc[mask] + "missing_email;"

    # 3. Date invalide
    mask = df["created_at"].isna()
    errors.loc[mask] = errors.loc[mask] + "invalid_created_at;"

    # 4. Customer ID dupliqué
    mask = df["customer_id"].duplicated(keep=False)
    errors.loc[mask] = errors.loc[mask] + "duplicate_customer_id;"

    # Ajouter les erreurs au DataFrame
    df["rejection_reason"] = errors

    # Une ligne est rejetée si elle possède au moins une erreur
    rejected_mask = df["rejection_reason"] != ""

    rejected = original_df.loc[rejected_mask].copy()
    rejected["rejection_reason"] = df.loc[
        rejected_mask, "rejection_reason"
    ].values

    valid = df.loc[~rejected_mask].copy()

    print()
    print("   DATA QUALITY REPORT")
    print("   -------------------")
    print(f"   Input rows:       {len(df)}")
    print(f"   Valid rows:       {len(valid)}")
    print(f"   Rejected rows:    {len(rejected)}")

    print()
    print(
        f"   Missing customer_id: "
        f"{(errors.str.contains('missing_customer_id')).sum()}"
    )

    print(
        f"   Missing email:       "
        f"{(errors.str.contains('missing_email')).sum()}"
    )

    print(
        f"   Invalid date:        "
        f"{(errors.str.contains('invalid_created_at')).sum()}"
    )

    print(
        f"   Duplicate ID:        "
        f"{(errors.str.contains('duplicate_customer_id')).sum()}"
    )

    return valid, rejected


def load_valid(df):
    print()
    print("3. Chargement des données valides...")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO raw.customers (
                customer_id,
                first_name,
                last_name,
                email,
                city,
                country,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO NOTHING;
            """,
            (
                int(row["customer_id"]),
                row["first_name"],
                row["last_name"],
                row["email"],
                row["city"],
                row["country"],
                row["created_at"],
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} lignes valides chargées.")


def load_rejected(df):
    print("4. Chargement des données rejetées...")

    if df.empty:
        print("   Aucune donnée rejetée.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO raw.rejected_customers (
                customer_id,
                first_name,
                last_name,
                email,
                city,
                country,
                created_at,
                rejection_reason
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id, rejection_reason) DO NOTHING;
            """,
            (
                row["customer_id"],
                row["first_name"],
                row["last_name"],
                row["email"],
                row["city"],
                row["country"],
                row["created_at"],
                row["rejection_reason"],
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"   {len(df)} lignes rejetées enregistrées.")


def main():

    df = extract()

    valid, rejected = transform(df)

    load_valid(valid)

    load_rejected(rejected)

    print()
    print("ETL terminé !")


if __name__ == "__main__":
    main()