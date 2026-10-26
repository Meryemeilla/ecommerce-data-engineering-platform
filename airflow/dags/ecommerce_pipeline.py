
import subprocess
import sys

import pendulum
from airflow.sdk import dag, task


PROJECT_ROOT = "/opt/ecommerce"
DATABASES_DIR = f"{PROJECT_ROOT}/src/database"


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
    description="Pipeline ETL e-commerce avec tâches Airflow séparées",
    start_date=pendulum.datetime(
        2026, 10, 1,
        tz="Africa/Casablanca",
    ),
    schedule="0 2 * * *",
    catchup=False,
    tags=["ecommerce", "etl", "data-quality"],
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
    analytics = refresh_analytics()
    quality = data_quality_checks()

    prepare >> staging >> analytics >> quality


ecommerce_pipeline()
