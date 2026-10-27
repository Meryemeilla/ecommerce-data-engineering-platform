# E-commerce Data Engineering Platform

An end-to-end data engineering project that ingests e-commerce CSV data, validates and transforms records with Python and SQL, and builds analytics-ready datasets in PostgreSQL. Apache Airflow orchestrates the ETL workflow, while Docker provides the local development environment.

## Project Overview

This project simulates an e-commerce data platform that transforms operational data into structured, reliable datasets for business analysis.

The pipeline handles four entities:

- Customers
- Products
- Orders
- Order items

It organizes data into three PostgreSQL schemas: `raw`, `staging`, and `analytics`.

## Architecture

```text
                  E-commerce CSV Files
                           |
                           v
                  Python Ingestion
                  Validation & DQ
                           |
                           v
                    PostgreSQL
                       raw
                           |
                           v
                SQL Transformations
                           |
                           v
                    PostgreSQL
                     staging
                           |
                           v
                 Analytics Loading
                           |
                           v
                    PostgreSQL
                    analytics
                           |
                           v
                 Business Reporting

             Apache Airflow orchestrates
                 the entire workflow
```

### Data Layers

| Layer | Purpose |
|---|---|
| `raw` | Stores ingested operational data and rejected records. |
| `staging` | Contains cleaned, validated, and transformed datasets. |
| `analytics` | Provides business-oriented tables for revenue analysis. |

## Tech Stack

- **Language:** Python 3.12
- **Database:** PostgreSQL 16
- **Data transformation:** SQL and Python
- **Orchestration:** Apache Airflow 3.3.2
- **Containerization:** Docker and Docker Compose
- **Automated testing:** pytest and pytest-cov
- **Version control:** Git and GitHub

## Key Features

- CSV ingestion and record validation.
- Rejected-record handling for invalid input data.
- Layered data architecture using PostgreSQL schemas.
- SQL transformations and relational joins.
- Customer and order revenue analytics.
- Automated data quality checks based on business rules.
- Scheduled ETL orchestration with Apache Airflow.
- Error propagation from failed Python scripts to Airflow tasks.
- Analytics loading using PostgreSQL conflict-handling logic.
- Automated tests for data quality and subprocess error handling.

## Analytics Datasets

### `analytics.order_revenue`

Provides order-level information, including:

- Order ID
- Order date
- Order status
- Calculated order total

### `analytics.customer_revenue`

Provides customer-level metrics, including:

- Customer ID
- Customer name
- Revenue from delivered orders
- Number of delivered orders

These datasets can support revenue reporting, customer analysis, and order-status monitoring.

## Data Quality

The project implements 11 automated SQL checks covering:

- Customers without email addresses or first names.
- Products without names.
- Negative product prices or stock quantities.
- Orders without valid customers.
- Invalid or missing order statuses.
- Order items referencing nonexistent orders or products.
- Invalid quantities.
- Negative unit prices.

The quality script reports the number of detected anomalies and exits with a nonzero status when anomalies are found. This allows failures to propagate to the orchestration layer.

## Validation Results

The following results were observed during local validation against the current sample dataset.

| Validation | Result |
|---|---:|
| Automated Python tests | 9 passed |
| Overall test coverage | 98% |
| Data quality rules | 11 |
| Detected data quality anomalies | 0 |
| Staging tables checked for duplicate IDs | 0 duplicates |
| Revenue from delivered orders | 700.00 |
| Revenue reconciliation | All three totals matched |

The delivered revenue was independently calculated from staging order items, order-level analytics, and customer-level analytics. Each calculation returned **700.00**.

A manual Airflow pipeline rerun also completed successfully. Row counts remained unchanged across the six staging and analytics tables inspected.

These results validate the current sample dataset and tested scenarios; they do not imply exhaustive integration testing for every possible input or failure condition.

## Airflow Orchestration

The DAG is named `ecommerce_pipeline`.

It contains four sequential tasks:

1. `prepare_tables` — creates the required staging and analytics tables.
2. `load_staging` — loads transformed data into staging tables.
3. `refresh_analytics` — refreshes the analytics datasets.
4. `data_quality_checks` — executes the SQL-based quality checks.

The DAG is configured to run daily at 02:00 in the `Africa/Casablanca` timezone.

Airflow manages task dependencies and records execution states. A failed script causes its corresponding task to fail, preventing downstream tasks from running under the default success-based dependency rule.

## Project Structure

```text
ecommerce-data-platform/
├── airflow/
│   ├── dags/
│   │   └── ecommerce_pipeline.py
│   └── docker-compose.yml
├── data/
│   └── raw/
├── src/
│   ├── ingestion/
│   └── database/
├── tests/
│   ├── test_data_quality.py
│   └── test_pipeline_errors.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pytest.ini
└── README.md
```

This tree highlights the main components. Additional files may exist within the source and configuration directories.

## Getting Started

### Prerequisites

- Git
- Docker Desktop with Docker Compose
- Python 3.12 for local testing

### 1. Clone the repository

```bash
git clone https://github.com/Meryemeilla/ecommerce-data-engineering-platform.git
cd ecommerce-data-engineering-platform
```

### 2. Configure environment variables

Create a local `.env` file using `.env.example` as a template.

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Review `.env.example` and configure the required database credentials and connection settings in `.env`. Do not commit real credentials.

### 3. Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

Check the container status:

```bash
docker compose ps
```

### 4. Start Airflow

From the project root, start the Airflow Compose configuration:

```bash
docker compose -f airflow/docker-compose.yml up -d
```

Open the Airflow interface:

[http://localhost:8080](http://localhost:8080)

Use the credentials configured by the local Airflow setup.

### 5. Run the pipeline

In Airflow:

1. Locate `ecommerce_pipeline`.
2. Enable the DAG if necessary.
3. Trigger a manual run.
4. Inspect the four task states and their logs.

The PostgreSQL database, environment variables, and required tables must be configured before running the pipeline.

### 6. Run automated tests

Create and activate a virtual environment if needed, install the project's Python dependencies, then run:

```bash
python -m pytest tests/ -v
```

To generate a coverage report:

```bash
python -m pytest tests/ --cov --cov-report=term-missing
```

The latest recorded test run contained nine passing tests and 98% overall coverage.

## Security

- Keep `.env` out of version control.
- Use placeholder values in `.env.example`.
- Never publish database passwords, API keys, or other secrets.
- Review staged Git changes before pushing to GitHub.

## Roadmap

- [ ] Add database integration tests.
- [ ] Test data quality failure propagation through the real Airflow task.
- [ ] Add stronger idempotence and data reconciliation tests.
- [ ] Introduce dbt for transformation management and testing.
- [ ] Build a BI dashboard for revenue and customer metrics.
- [ ] Add continuous integration with GitHub Actions.
- [ ] Add architecture diagrams and execution screenshots.

## Project Status

**Core ETL workflow implemented and locally validated against the current sample dataset.**

The project demonstrates layered data modeling, SQL transformations, automated data quality checks, Airflow orchestration, Docker-based development, and Python testing. Further integration testing and observability improvements remain planned.
