FROM apache/airflow:3.3.2-python3.12

USER airflow

RUN pip install --no-cache-dir \
    psycopg2-binary \
    python-dotenv \
    dbt-core==1.12.6 \
    dbt-postgres==1.11.0
