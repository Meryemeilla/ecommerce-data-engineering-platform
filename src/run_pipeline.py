import subprocess
import sys

from pathlib import Path
import logging
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASES_DIR = PROJECT_ROOT / "src" / "database"

LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

log_file = LOGS_DIR / (
    f"pipeline_{datetime.now():%Y%m%d_%H%M%S}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

SCRIPTS = [
    # 1. Création des tables staging
    "create_staging.py",
    "create_staging_products.py",
    "create_staging_orders.py",
    "create_staging_order_items.py",

    # 2. Création des tables analytics
    "create_analytics_tables.py",
    "create_analytics_customer_revenue.py",

    # 3. Chargement des données staging
    "load_staging_customers.py",
    "load_staging_products.py",
    "load_staging_orders.py",
    "load_staging_order_items.py",

    # 4. Calcul des indicateurs analytiques
    "load_analytics_order_revenue.py",
    "load_analytics_customer_revenue.py",
    "data_quality.py",
]



def run_script(script_name):
    script_path = DATABASES_DIR / script_name

    logger.info("Début d'exécution : %s", script_name)
    start_time = datetime.now()

    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            cwd=PROJECT_ROOT,
        )

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(
            "Succès : %s | Durée : %.2f secondes",
            script_name,
            duration,
        )

    except subprocess.CalledProcessError:
        logger.exception("Échec du script : %s", script_name)
        raise




def main():
    pipeline_start = datetime.now()
    logger.info("========== DÉBUT DU PIPELINE ==========")

    try:
        for script in SCRIPTS:
            run_script(script)

        duration = (datetime.now() - pipeline_start).total_seconds()

        logger.info(
            "========== PIPELINE TERMINÉ AVEC SUCCÈS | "
            "Durée totale : %.2f secondes ==========",
            duration,
        )
        print("\nPipeline terminé avec succès !")

    except subprocess.CalledProcessError as error:
        logger.error(
            "Pipeline interrompu. Code de retour : %s",
            error.returncode,
        )
        print(
            f"\nÉchec du pipeline : {error.cmd}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
