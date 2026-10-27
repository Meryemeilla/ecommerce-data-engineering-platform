# E-commerce Data Engineering Platform

An end-to-end data engineering project built with Python, PostgreSQL, Docker, and Apache Airflow. The project demonstrates how to ingest e-commerce CSV data, validate and transform records, and produce analytics-ready datasets through an orchestrated ETL pipeline.

## Project Overview

This project simulates a small e-commerce data platform designed to transform raw operational data into reliable datasets for business reporting.

The pipeline processes customers, products, orders, and order items through three data layers: `raw`, `staging`, and `analytics`.

## Architecture

```text
CSV Files
   |
   v
Python Ingestion
   |
   v
PostgreSQL - raw
   |
   v
Staging Transformations
   |
   v
PostgreSQL - staging
   |
   v
Analytics Tables
   |
   v
Data Quality Checks
```

Apache Airflow orchestrates the workflow and manages task dependencies and execution status.

## Tech Stack

- **Language:** Python
- **Database:** PostgreSQL
- **Data Processing:** SQL, Python
- **Orchestration:** Apache Airflow
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest

## Key Features

- CSV ingestion and record validation
- Rejected-record handling for invalid input data
- Layered data architecture using `raw`, `staging`, and `analytics` schemas
- Customer revenue and order revenue analytics
- Automated data quality checks
- Scheduled ETL orchestration with Apache Airflow
- Idempotent analytics loading using PostgreSQL `ON CONFLICT ... DO UPDATE`
- Python tests for data quality configuration and subprocess error handling

## Analytics

The project currently provides two analytics tables:

- `analytics.customer_revenue`: delivered revenue and delivered order counts by customer.
- `analytics.order_revenue`: calculated order totals and order statuses.

These datasets can support reporting on delivered revenue, customer activity, and order status distribution.

## Data Quality

The data quality script checks key business rules, including:

- Customers without email addresses or first names
- Products without names or with negative prices or stock
- Orders without valid customers or with invalid statuses
- Order items without valid orders or products
- Invalid quantities and negative unit prices

The latest validation on the current sample dataset reported **11 checks and 0 detected anomalies**.

## Pipeline Orchestration

The Airflow DAG is named `ecommerce_pipeline` and contains four sequential tasks:

1. `prepare_tables`
2. `load_staging`
3. `refresh_analytics`
4. `data_quality_checks`

The DAG is configured with a daily schedule. The latest six runs inspected were successful. Analytics validation queries also found no discrepancies between the stored revenue metrics and the values recalculated from the staging data.

## Project Structure

```text
.
├── airflow/
│   └── dags/
│       └── ecommerce_pipeline.py
├── data/
│   └── raw/
├── src/
│   ├── ingestion/
│   └── database/
├── tests/
├── docker-compose.yml
├── pytest.ini
└── README.md
```

*The structure above summarizes the main project components; verify it against the repository before publishing.*

## Getting Started

### Prerequisites

- Python 3.12
- Docker Desktop with Docker Compose
- Git

### Setup

1. Clone the repository.
2. Create a local `.env` file based on `.env.example`.
3. Configure the required database environment variables.
4. Start the services using the repository's Docker Compose configuration.
5. Run the pipeline using the configured Airflow DAG.
6. Run the tests locally:

```bash
python -m pytest tests/ -v
```

Follow the Docker Compose configuration and project scripts for the exact startup and database initialization commands.

## Security

- Never commit `.env` files or real credentials.
- Keep `.env.example` limited to placeholder values.
- Review the repository for secrets before pushing to GitHub.

## Roadmap

- [ ] Add integration tests for database transformations
- [ ] Verify Airflow task failure behavior when data quality checks fail
- [ ] Add dbt transformations, tests, and documentation
- [ ] Build a BI dashboard
- [ ] Add CI/CD with GitHub Actions

## Project Status

**Core pipeline implemented and validated against the current sample dataset.** Further integration testing, documentation, and portfolio improvements are planned.

