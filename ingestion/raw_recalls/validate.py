import sys
sys.path.append('/opt/airflow/ingestion')

from utils.bigquery import get_bq_client, validate_bq_check, table_exists
from utils.logger import get_logger
from raw_recalls.config import (
    GCP_PROJECT, BQ_DATASET, BQ_TABLE,
    VALIDATION_CHECKS,
)

logger = get_logger(__name__)

TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"


def run_validation():
    """
    Runs all data quality checks defined in config.py
    against the raw_recalls BigQuery table.
    Raises ValueError if any check fails.
    Called by Airflow DAG task.
    """
    client = get_bq_client(GCP_PROJECT)

    if not table_exists(client, GCP_PROJECT, BQ_DATASET, BQ_TABLE):
        raise ValueError(f"Table {TABLE_ID} does not exist — was ingestion run?")

    failed = []
    for check_name, query_template in VALIDATION_CHECKS.items():
        query = query_template.format(table_id=TABLE_ID)
        passed = validate_bq_check(client, check_name, query)
        if not passed:
            failed.append(check_name)

    if failed:
        raise ValueError(
            f"Validation failed for {TABLE_ID}. "
            f"Failed checks: {', '.join(failed)}"
        )

    logger.info(f"All validation checks passed for {TABLE_ID}")


if __name__ == "__main__":
    run_validation()