# E-commerce Data Engineering Platform

An end-to-end data engineering project built with Python, PostgreSQL, Docker, Apache Airflow and automated testing.

## Project Overview

This project implements an e-commerce data pipeline designed to ingest raw CSV data, validate records, load structured staging tables, generate analytical datasets and enforce data quality rules.

The pipeline is orchestrated with Apache Airflow and includes automated integration and unit tests.

## Architecture

```text
CSV Files
    |
    v
Python Data Ingestion
    |
    v
PostgreSQL - RAW Layer
    |
    v
Data Validation
    |
    v
PostgreSQL - STAGING Layer
    |
    v
SQL Transformations
    |
    v
PostgreSQL - ANALYTICS Layer
    |
    v
Data Quality Checks
```

Apache Airflow orchestrates the pipeline execution and manages retries and task timeouts.

## Tech Stack

- **Programming:** Python
- **Database:** PostgreSQL, SQL
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Apache Airflow 3
- **Testing:** Pytest, PostgreSQL integration tests
- **Version Control & CI:** Git, GitHub Actions

## Key Features

- CSV data ingestion and validation
- Rejected-record handling
- Raw, staging and analytics data layers
- SQL transformations and business analytics
- Referential integrity through PostgreSQL foreign keys
- Customer and order revenue analytics
- Automated data quality checks
- Idempotent analytics loading
- Pipeline orchestration with Apache Airflow
- Automatic retries and execution timeouts
- Unit and PostgreSQL integration tests
- Continuous integration with GitHub Actions

## Project Structure

```text
ecommerce-data-engineering-platform/
│
├── airflow/
│   ├── dags/
│   │   └── ecommerce_pipeline.py
│   └── Dockerfile
│
├── data/
│   └── raw/
│
├── src/
│   ├── ingestion/
│   ├── database/
│   └── run_pipeline.py
│
├── tests/
│   ├── integration/
│   │   └── test_postgres_integration.py
│   ├── conftest.py
│   ├── test_data_quality.py
│   └── test_pipeline_errors.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── docker-compose.yml
├── requirements-test.txt
├── .env.example
├── .gitignore
└── README.md
```

## Data Architecture

The project uses three logical data layers:

**1. Raw Layer**

- Stores ingested source data.
- Preserves raw records.
- Handles invalid and rejected records.

**2. Staging Layer**

- Stores validated and structured data.
- Applies data cleaning and transformations.
- Enforces primary keys and foreign key relationships.

**3. Analytics Layer**

- Generates analytical datasets.
- Calculates order revenue and customer revenue.
- Supports business reporting and analytical queries.

## Airflow Orchestration

The main DAG is `ecommerce_pipeline`.

It coordinates four tasks:

1. `prepare_tables`
2. `load_staging`
3. `refresh_analytics`
4. `data_quality_checks`

**Execution configuration:**

- Schedule: Daily at 02:00
- Timezone: Africa/Casablanca
- Retries: 2
- Retry delay: 2 minutes
- Task execution timeout: 15 minutes
- Catchup: Disabled

## Testing

The project includes unit tests and PostgreSQL integration tests.

Run the test suite locally:

```bash
python -m pip install -r requirements-test.txt
python -m pytest -v
```

The integration tests use a dedicated `ecommerce_test` database to avoid modifying development data.

**Latest local test result: 11 passed.**

GitHub Actions automatically executes the test suite on pushes and pull requests targeting `main`.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Meryemeilla/ecommerce-data-engineering-platform.git
cd ecommerce-data-engineering-platform
```

2. Create and activate a Python virtual environment.

3. Install the required dependencies.

4. Copy `.env.example` to `.env` and configure your local database credentials.

5. Start PostgreSQL using Docker Compose.

6. Create the dedicated `ecommerce_test` database and configure its credentials.

7. Run the data pipeline or use the configured Airflow DAG.

**Security:** Never commit `.env` files, database passwords or other credentials.

## Roadmap

- [ ] Add dbt for modular SQL transformations and documentation
- [ ] Build a BI dashboard for business analytics
- [ ] Expand automated testing and test coverage
- [ ] Add advanced monitoring and pipeline observability
- [ ] Improve CI/CD workflows

## Project Status

Active portfolio project focused on practical data engineering concepts, database design, pipeline orchestration, data quality and automated testing.