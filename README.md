# 🚗 Automotive Aftersales Data Pipeline

A production-grade batch data pipeline for automotive dealer aftersales analytics, built as part of a Data Engineering portfolio project.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Data Model](#data-model)
- [Pipeline Design](#pipeline-design)
- [CI/CD](#cicd)
- [DAGs](#dags)
- [dbt Models](#dbt-models)
- [Data Quality](#data-quality)
- [Monitoring & Alerts](#monitoring--alerts)

---

## Overview

This project implements an end-to-end batch data pipeline for **automotive dealer aftersales data** in the Indonesian market. It ingests daily transactional data from a custom-built Dummy API, validates and transforms it through multiple layers, and serves analytics-ready tables in BigQuery.

The pipeline simulates a real-world scenario where a data engineering team supports an automotive company's analytics needs — tracking service orders, sales transactions, warranty claims, and dealer/brand performance across Indonesia.

**Key highlights:**
- Daily ingestion of 6 data domains with ~100–250 records/day
- 90+ days of historical data backfilled
- Full data quality validation at every layer
- Automated dbt transformation triggered by Airflow ExternalTaskSensor
- Slack alerting on task failures
- CI/CD via GitHub Actions with automatic server deployment

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tencent Cloud Lighthouse                      │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────────────────────────┐   │
│  │  Dummy API   │    │         Apache Airflow               │   │
│  │  (FastAPI)   │───▶│                                      │   │
│  │  Port: 8000  │    │  DAG 1: raw_auto_dummy_api_dag       │   │
│  └──────────────┘    │  DAG 2: transform_auto_dbt_dag       │   │
│                      └──────────────┬───────────────────────┘   │
│                                     │                            │
│                      ┌──────────────▼───────────────────────┐   │
│                      │         dbt Core                      │   │
│                      │  (runs inside Airflow container)      │   │
│                      └──────────────┬───────────────────────┘   │
│                                     │                            │
└─────────────────────────────────────┼───────────────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
                    │         Google BigQuery             │
                    │                                     │
                    │  raw             (ingestion layer)  │
                    │  staging         (dbt tables)       │
                    │  consumption     (dbt tables)       │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
                    │         Slack Notifications         │
                    │         (task failures)             │
                    └─────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow |
| Transformation | dbt Core + dbt-bigquery |
| Data Warehouse | Google BigQuery |
| Dummy API | FastAPI |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Server | Tencent Cloud Lighthouse |
| Language | Python |
| Notifications | Slack Bot / Slack API |

---

## Project Structure

```
project-pipeline/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline
├── airflow/
│   ├── dags/
│   │   ├── common/
│   │   │   ├── __init__.py
│   │   │   └── callbacks.py        # Slack notification callbacks
│   │   ├── raw_auto_dummy_api_dag.py   # Ingestion DAG
│   │   └── transform_auto_dbt_dag.py  # dbt transformation DAG
│   └── logs/
├── dbt/
│   └── auto_project/
│       ├── dbt_project.yml
│       ├── profiles.yml
│       ├── macros/
│       │   └── generate_schema_name.sql
│       └── models/
│           ├── staging/
│           │   ├── sources.yml
│           │   ├── schema.yml
│           │   ├── stg_vehicles.sql
│           │   ├── stg_spare_parts.sql
│           │   ├── stg_service_orders.sql
│           │   ├── stg_service_order_items.sql
│           │   ├── stg_sales_orders.sql
│           │   └── stg_warranty_claims.sql
│           └── consumption/
│               ├── schema.yml
│               ├── dim_vehicles.sql
│               ├── dim_dealers.sql
│               ├── fct_service_orders.sql
│               ├── fct_sales_orders.sql
│               ├── fct_warranty_claims.sql
│               ├── mart_dealer_performance.sql
│               └── mart_brand_performance.sql
├── ingestion/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── bigquery.py             # Generic BQ utilities
│   │   ├── dummy_api.py            # Generic API utilities
│   │   └── logger.py              # Shared logger
│   ├── raw_vehicles/
│   │   ├── config.py
│   │   ├── schema.py
│   │   ├── fetch.py
│   │   └── validate.py
│   ├── raw_spare_parts/
│   ├── raw_service_orders/
│   ├── raw_service_order_items/
│   ├── raw_sales_orders/
│   └── raw_warranty_claims/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Data Sources

All data is generated by a custom-built **Dummy API** (FastAPI) simulating an automotive dealer management system in Indonesia.

**Dummy API repo:** [de-portfolio-mock-api](https://github.com/ferdianmaulana/de-portfolio-mock-api)

### Endpoints

| Endpoint | Type | Records/day | Write Mode |
|---|---|---|---|
| `GET /vehicles` | Master | 500 (static) | TRUNCATE |
| `GET /spare-parts` | Master | ~25 (static) | TRUNCATE |
| `GET /service-orders?date=YYYY-MM-DD` | Transaction | 20–50 | APPEND |
| `GET /service-order-items?date=YYYY-MM-DD` | Transaction | 50–150 | APPEND |
| `GET /sales-orders?date=YYYY-MM-DD` | Transaction | 10–30 | APPEND |
| `GET /warranty-claims?date=YYYY-MM-DD` | Transaction | 5–15 | APPEND |

### Market Scope

- **10 brands:** Toyota, Honda, Suzuki, Daihatsu, Mitsubishi, Nissan, Hyundai, Kia, BMW, Mercedes, Volkswagen
- **12 dealers** across Jakarta, Surabaya, Bandung, Medan, Makassar, Semarang, Yogyakarta, Palembang
- **Model years:** 2018–2024

---

## Data Model

### BigQuery Datasets

| Dataset | Layer | Description |
|---|---|---|
| `raw` | Raw | Direct ingestion from Dummy API — no transformation |
| `staging` | Staging | Deduplicated, cleaned, and type-cast tables |
| `consumption` | Consumption | Business-ready dimension, fact, and mart tables |

### Raw Layer Tables

```
raw.vehicles              — Master vehicle registry
raw.spare_parts           — Parts catalog
raw.service_orders        — Daily workshop job orders
raw.service_order_items   — Parts & labor per service order
raw.sales_orders          — Vehicle sales transactions
raw.warranty_claims       — Warranty claim submissions
```

### Staging Layer (dbt Tables)

```
staging.stg_vehicles              — Deduplicated vehicles
staging.stg_spare_parts           — Deduplicated parts catalog
staging.stg_service_orders        — Deduplicated service orders
staging.stg_service_order_items   — Deduplicated line items
staging.stg_sales_orders          — Deduplicated sales
staging.stg_warranty_claims       — Deduplicated warranty claims
```

### Consumption Layer (dbt Tables)

```
consumption.dim_vehicles           — Vehicle dimension + warranty status + brand segment
consumption.dim_dealers            — Dealer dimension + tier classification
consumption.fct_service_orders     — Completed service order facts
consumption.fct_sales_orders       — Sales order facts
consumption.fct_warranty_claims    — Warranty claim facts
consumption.mart_dealer_performance — Monthly dealer KPIs
consumption.mart_brand_performance  — Monthly brand KPIs
```

### Entity Relationships

```
dim_vehicles ◄──────────────────────────────────────────┐
dim_dealers  ◄─────────────────────────────────────┐    │
                                                    │    │
raw.service_orders ──► fct_service_orders ──────────┘    │
raw.sales_orders   ──► fct_sales_orders ─────────────────┘
raw.warranty_claims──► fct_warranty_claims

fct_service_orders ──┐
fct_sales_orders   ──┼──► mart_dealer_performance
fct_warranty_claims──┘──► mart_brand_performance
```

---

## Pipeline Design

### DAG 1: `raw_auto_dummy_api_dag`

**Schedule:** `0 1 * * *` (01:00 Jakarta time daily)

**Task flow:**
```
fetch_vehicles ──► validate_vehicles ──┐
                                       ├──► fetch_service_orders ──► validate ──► fetch_items ──► validate_items
fetch_spare_parts ──► validate_spare ──┤
                                       ├──► fetch_sales_orders ──► validate_sales
                                       └──► fetch_warranty_claims ──► validate_warranty
```

- Master data (vehicles, spare parts) runs in parallel first
- Transactions run in parallel after master data completes
- Service order items depend on service orders (sequential)
- Each table is a separate task — failures are isolated

### DAG 2: `transform_auto_dbt_dag`

**Schedule:** `30 1 * * *` (01:30 Jakarta time daily)

**Trigger:** `ExternalTaskSensor` — waits for `raw_auto_dummy_api_dag` to succeed before starting.

**Task flow:**
```
wait_for_ingestion >> dbt_debug >> dbt_deps
    ↓
stg_vehicles / stg_spare_parts / stg_service_orders / stg_sales_orders / stg_warranty_claims
    ↓ (run + test per model)
dim_vehicles / dim_dealers
    ↓
fct_service_orders / fct_sales_orders / fct_warranty_claims
    ↓
mart_dealer_performance / mart_brand_performance
    ↓
dbt_docs_generate
```

Each dbt model has its own `run` + `test` task pair — failures are isolated to the specific model.

### Ingestion Module Design

Each table has its own module with 4 files following a consistent pattern:

```
raw_<table>/
├── config.py    — BQ config, API endpoint, write mode, validation checks
├── schema.py    — Explicit BigQuery schema with column descriptions
├── fetch.py     — Fetch from API, load to BigQuery
└── validate.py  — Run validation checks against BigQuery
```

Shared utilities in `utils/`:

```python
# Generic API caller — works for any REST API
call_api_with_retry(base_url, endpoint, params, ...)

# Generic BigQuery loader — works for any table
load_to_bq(client, rows, project, dataset, table, write_mode, schema)

# Generic validation runner — runs checks from config.py
run_validations(project, dataset, table, checks, extra_checks)
```

---

## CI/CD

Every push to `main` triggers a GitHub Actions workflow that:

1. SSHs into the Lighthouse server
2. Fixes file permissions
3. Pulls latest code via `git pull`
4. Writes secrets to server (GCP credentials, env vars)
5. Stops all containers (`docker compose down`)
6. Rebuilds Docker image from scratch (`--no-cache`)
7. Re-initializes Airflow DB (`airflow-init`)
8. Starts all services (`docker compose up -d`)

---

## DAGs

### Ingestion DAG — `raw_auto_dummy_api_dag`

| Property | Value |
|---|---|
| Schedule | `0 1 * * *` (01:00 Jakarta time) |
| Retries | 2 per task |
| Retry delay | 5 minutes |
| Max active runs | 1 |
| Tags | batch, automotive, aftersales, sales, daily |

### dbt DAG — `transform_auto_dbt_dag`

| Property | Value |
|---|---|
| Schedule | `30 1 * * *` (01:30 Jakarta time) |
| Trigger | ExternalTaskSensor on ingestion DAG |
| Retries | 1 per task |
| Max active runs | 1 |
| Tags | dbt, automotive, transformation, daily |

---

## dbt Models

### Staging Layer

All staging models follow the same pattern:
- Read from `raw` dataset
- Deduplicate using `ROW_NUMBER()` partitioned by the unique ID, ordered by `ingested_at DESC`
- Cast all columns to explicit types
- Clean string columns with `TRIM()` and `UPPER()` where applicable
- Materialized as **tables**

### Consumption Layer

**Dimensions:**

| Model | Description | Key Fields |
|---|---|---|
| `dim_vehicles` | Vehicle master + warranty status + brand segment + age | `vehicle_id`, `is_under_warranty`, `brand_segment` |
| `dim_dealers` | Dealer master + tier classification | `dealer_id`, `dealer_tier` |

**Facts:**

| Model | Description | Key Metrics |
|---|---|---|
| `fct_service_orders` | Completed service orders | `total_cost`, `actual_hours`, `completed_on_time` |
| `fct_sales_orders` | Vehicle sales | `final_price`, `discount_pct`, `delivery_lead_days` |
| `fct_warranty_claims` | Warranty claims | `claim_amount`, `approved_amount`, `approval_rate_pct` |

**Marts:**

| Model | Description | Business Questions Answered |
|---|---|---|
| `mart_dealer_performance` | Monthly dealer KPIs | Which dealers generate most revenue? What is the warranty claim rate per dealer? |
| `mart_brand_performance` | Monthly brand KPIs | Which brands have the highest repair rate? What is the warranty claim rate per brand? |

---

## Data Quality

### Raw Layer Validation (Python + BigQuery SQL)

Each table has validation checks defined in `config.py` and executed via `run_validations()` after ingestion:

| Check type | Example |
|---|---|
| Null checks | `order_id IS NULL` |
| Range checks | `model_year < 2018 OR model_year > 2024` |
| Accepted values | `status NOT IN ('Open', 'In Progress', 'Completed', 'Cancelled')` |
| Minimum row count | `COUNT(*) < 10` |
| Today's data exists | `COUNT(*) = 0 WHERE order_date = '{today}'` |

If any check fails, the Airflow task raises a `ValueError` and the downstream tasks are blocked.

### Staging + Consumption Layer Validation (dbt tests)

Each model has schema tests defined in `schema.yml`:

| Test | Models |
|---|---|
| `not_null` | All primary keys and required fields |
| `unique` | All primary keys |
| `accepted_values` | Categorical fields (status, fuel_type, sale_type, etc.) |

---

## Monitoring & Alerts

Slack notifications are sent to `#all-airflow-notification` for:
- ❌ **Task failure** — includes DAG name, task name, execution date, error message, and a direct link to the logs

Callbacks are configured at the `default_args` level so every task in both DAGs automatically sends failure alerts via Slack Bot API.