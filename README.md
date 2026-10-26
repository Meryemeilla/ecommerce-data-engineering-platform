# E-commerce Data Engineering Platform

An end-to-end data engineering project built with Python, PostgreSQL, Docker and Apache Airflow.

## Project Overview

This project implements an e-commerce data pipeline to ingest raw CSV data, validate records, load staging tables, generate analytics datasets and perform data quality checks.

## Architecture

CSV files → Python ingestion → PostgreSQL raw schema → staging transformations → analytics tables → data quality checks.

Apache Airflow orchestrates the pipeline through separate tasks.

## Tech Stack

- Python
- PostgreSQL and SQL
- Docker and Docker Compose
- Apache Airflow

## Features

- CSV data ingestion
- Data validation and rejected-record handling
- Raw, staging and analytics layers
- Customer and order revenue analytics
- Data quality checks
- Scheduled pipeline orchestration with Airflow

## Project Structure

- `src/ingestion/` — CSV ingestion scripts
- `src/database/` — database setup, transformations and data quality checks
- `airflow/dags/` — Airflow DAG
- `data/raw/` — sample CSV files
- `docker-compose.yml` — PostgreSQL configuration

## Setup

1. Clone this repository.
2. Copy `.env.example` to `.env`.
3. Configure your local database credentials in `.env`.
4. Start PostgreSQL using Docker Compose.
5. Run the pipeline according to the project configuration.

**Security:** Never commit `.env` or real credentials.

## Roadmap

- [ ] Improve error handling and automated tests
- [ ] Add dbt transformations, tests and documentation
- [ ] Build a BI dashboard
- [ ] Add CI/CD with GitHub Actions

## Project Status

Portfolio project under active development.
