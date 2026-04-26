import sys
sys.path.append('/opt/airflow/ingestion')

from utils.bigquery import run_validations
from raw_vehicles.config import GCP_PROJECT, BQ_DATASET, BQ_TABLE, VALIDATION_CHECKS


def run_validation():
    run_validations(GCP_PROJECT, BQ_DATASET, BQ_TABLE, VALIDATION_CHECKS)


if __name__ == "__main__":
    run_validation()