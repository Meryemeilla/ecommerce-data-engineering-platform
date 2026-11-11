import subprocess
import sys

import pendulum
from airflow.sdk import dag, task


PROJECT_ROOT = "/opt/ecommerce"
DATABASES_DIR = f"{PROJECT_ROOT}/src/database"

DBT_PROJECT_DIR = "/opt/airflow/dbt/ecommerce_dbt"
DBT_PROFILES_DIR = "/opt/airflow/dbt_config"


def execute_scripts(script_names):
    """Exécute une liste de scripts Python dans l'ordre indiqué."""
    for script_name in script_names:
        script_path = f"{DATABASES_DIR}/{script_name}"

        subprocess.run(
            [sys.executable, script_path],
            check=True,
            cwd=PROJECT_ROOT,
        )


@dag(
    dag_id="ecommerce_pipeline",
    description="Pipeline ETL e-commerce avec Python, dbt et Airflow",
    start_date=pendulum.datetime(
        2026, 10, 1,
        tz="Africa/Casablanca",
    ),
    schedule="0 2 * * *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": pendulum.duration(minutes=2),
        "execution_timeout": pendulum.duration(minutes=15),
    },
    tags=["ecommerce", "etl", "dbt", "data-quality"],
)
def ecommerce_pipeline():

    @task
    def prepare_tables():
        execute_scripts([
            "create_staging.py",
            "create_staging_products.py",
            "create_staging_orders.py",
            "create_staging_order_items.py",
            "create_analytics_tables.py",
            "create_analytics_customer_revenue.py",
        ])

    @task
    def load_staging():
        execute_scripts([
            "load_staging_customers.py",
            "load_staging_products.py",
            "load_staging_orders.py",
            "load_staging_order_items.py",
        ])

    @task
    def dbt_build():
        """Construit les modèles dbt et exécute les tests."""
        subprocess.run(
            [
                "dbt",
                "build",
                "--project-dir", DBT_PROJECT_DIR,
                "--profiles-dir", DBT_PROFILES_DIR,
            ],
            check=True,
            cwd=DBT_PROJECT_DIR,
        )

    @task
    def refresh_analytics():
        execute_scripts([
            "load_analytics_order_revenue.py",
            "load_analytics_customer_revenue.py",
        ])

    @task
    def data_quality_checks():
        execute_scripts([
            "data_quality.py",
        ])

    prepare = prepare_tables()
    staging = load_staging()
    dbt = dbt_build()
    analytics = refresh_analytics()
    quality = data_quality_checks()

    prepare >> staging >> dbt >> analytics >> quality


ecommerce_pipeline()
