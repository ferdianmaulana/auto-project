import sys
sys.path.append('/opt/airflow/ingestion')

from datetime import date
from utils.bigquery import run_validations
from raw_warranty_claims.config import GCP_PROJECT, BQ_DATASET, BQ_TABLE, VALIDATION_CHECKS

TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"


def run_validation(logical_date: str = None):
    today = logical_date or str(date.today())
    run_validations(
        GCP_PROJECT, BQ_DATASET, BQ_TABLE,
        checks=VALIDATION_CHECKS,
        extra_checks={
            "today_data_exists": (
                f"SELECT IF(COUNT(*) = 0, 1, 0) "
                f"FROM `{TABLE_ID}` "
                f"WHERE claim_date = '{today}'"
            )
        }
    )


if __name__ == "__main__":
    run_validation()