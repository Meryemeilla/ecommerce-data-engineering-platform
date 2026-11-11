# E-commerce Data Engineering Platform

An end-to-end data engineering project built with **Python, PostgreSQL, dbt, Docker and Apache Airflow**.

The platform ingests raw e-commerce CSV data, validates records, transforms data through layered models, runs data quality tests and orchestrates the workflow with Airflow.

## Architecture

```text
                    CSV Files
                        |
                        v
              Python Data Ingestion
               Validation & Rejection
                        |
                        v
                 PostgreSQL RAW
                        |
                        v
               PostgreSQL STAGING
                        |
                        v
                  dbt Transformations
             Staging → Intermediate → Marts
                        |
                        v
                 dbt Data Tests
                        |
                        v
               Analytics Data Layer
                        |
                        v
             Python Data Quality Checks

             Apache Airflow orchestrates
                 the complete workflow
```

## Tech Stack

| Category | Technologies |
|---|---|
| Programming | Python 3.12 |
| Database | PostgreSQL 16, SQL |
| Transformation | dbt Core, dbt-postgres |
| Orchestration | Apache Airflow 3.3.2 |
| Containerization | Docker, Docker Compose |
| Testing | pytest, dbt tests, PostgreSQL integration tests |
| CI | GitHub Actions |
| Version Control | Git, GitHub |

## Key Features

- CSV ingestion using Python.
- Data validation and rejected-record handling.
- PostgreSQL RAW and STAGING layers.
- SQL transformations and analytical data models.
- Modular transformations using dbt.
- dbt staging, intermediate and mart models.
- Automated data quality tests with dbt.
- Customer, product and order analytics.
- Idempotent analytics loading.
- Airflow orchestration with retries and execution timeouts.
- Automated Python tests and PostgreSQL integration tests.
- Continuous integration with GitHub Actions.

## Data Architecture

The project separates data processing into logical layers.

### RAW

Stores source records ingested from CSV files, including the raw data used for subsequent processing.

### STAGING

Contains cleaned and validated data prepared for transformation and analysis.

### dbt Models

The dbt project organizes SQL transformations into three layers:

- **Staging:** source-oriented models that standardize and prepare data.
- **Intermediate:** reusable business transformations and enriched datasets.
- **Marts:** analytical models designed for reporting and business analysis.

### Analytics

Contains analytical datasets, including order revenue and customer revenue.

## dbt Implementation

The dbt project is located in:

```text
dbt/ecommerce_dbt/
```

It includes:

- 10 dbt models.
- 29 dbt data tests.
- Source definitions.
- Model documentation in YAML files.
- Custom SQL data tests.

Main model groups:

```text
models/
├── staging/
├── intermediate/
└── marts/
```

The dbt build command executes model materializations and tests:

```bash
dbt build
```

**Latest verified dbt result:**

```text
PASS=39
WARN=0
ERROR=0
SKIP=0
TOTAL=39
```

This represents 10 models and 29 tests successfully executed.

## Apache Airflow Orchestration

The main DAG is:

```text
ecommerce_pipeline
```

It orchestrates five sequential tasks:

| Task | Responsibility |
|---|---|
| `prepare_tables` | Create and prepare database tables |
| `load_staging` | Load validated data into staging |
| `dbt_build` | Build dbt models and execute dbt tests |
| `refresh_analytics` | Refresh Python-based analytics tables |
| `data_quality_checks` | Run additional data quality checks |

### DAG Configuration

- Schedule: Daily at 02:00
- Timezone: `Africa/Casablanca`
- Retries: 2
- Retry delay: 2 minutes
- Task execution timeout: 15 minutes
- Catchup: Disabled

**Latest verified manual execution:** all five Airflow tasks completed successfully.

## Automated Testing

The Python test suite includes:

| Test Category | Tests |
|---|---:|
| Data quality | 7 |
| Pipeline error handling | 2 |
| PostgreSQL integration | 2 |
| **Total** | **11** |

Run the tests locally:

```bash
python -m pip install -r requirements-test.txt
python -m pytest -v
```

The integration tests use a dedicated `ecommerce_test` database to avoid modifying the main development database.

**Latest verified local result:**

```text
11 passed
```

## Continuous Integration

GitHub Actions automatically runs the Python test suite on pushes and pull requests targeting the `main` branch.

The workflow uses:

- Python 3.12
- PostgreSQL 16 service
- A dedicated test database
- pytest

## Project Structure

```text
ecommerce-data-engineering-platform/
│
├── airflow/
│   ├── dags/
│   │   └── ecommerce_pipeline.py
│   ├── dbt_config/
│   │   └── profiles.yml
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── dbt/
│   └── ecommerce_dbt/
│       ├── models/
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── tests/
│       └── dbt_project.yml
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

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Meryemeilla/ecommerce-data-engineering-platform.git
cd ecommerce-data-engineering-platform
```

### 2. Configure environment variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Configure the database credentials and required environment variables locally.

### 3. Start PostgreSQL

Use the project's Docker Compose configuration to start the PostgreSQL service.

### 4. Run Python tests

Install dependencies and execute:

```bash
python -m pip install -r requirements-test.txt
python -m pytest -v
```

### 5. Run dbt

Configure the dbt profile with the appropriate PostgreSQL connection environment variables, then run:

```bash
dbt debug
dbt build
```

### 6. Run Airflow

Start the Airflow services using the configuration in the `airflow/` directory and trigger the `ecommerce_pipeline` DAG.

**Security:** Never commit `.env` files, database passwords, generated logs or other sensitive credentials.

## Current Project Status

| Component | Status |
|---|---|
| Python CSV ingestion | Completed |
| PostgreSQL RAW layer | Completed |
| PostgreSQL STAGING layer | Completed |
| dbt transformations | Completed |
| dbt tests | 29 passing |
| Python automated tests | 11 passing |
| PostgreSQL integration tests | Passing |
| GitHub Actions | Functional for Python tests |
| Airflow orchestration | Functional |
| Airflow + dbt integration | Successfully tested |
| BI dashboard | Planned |
| Extended CI/CD for dbt | Planned |

## Roadmap

- [ ] Add a BI dashboard using Power BI or Metabase.
- [ ] Extend GitHub Actions to validate and test dbt models.
- [ ] Improve pipeline monitoring and observability.
- [ ] Expand test coverage and documentation.
- [ ] Add further analytical use cases.

---

**Project Status:** Active portfolio project demonstrating practical data engineering workflows, SQL transformations, data quality, orchestration, automated testing and continuous integration.