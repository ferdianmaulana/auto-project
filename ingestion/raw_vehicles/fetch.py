import sys
sys.path.append('/opt/airflow/ingestion')

from datetime import datetime
from utils.dummy_api import call_api_with_retry, get_mock_api_url
from utils.bigquery import get_bq_client, load_to_bq
from utils.logger import get_logger
from raw_vehicles.config import (
    GCP_PROJECT, BQ_DATASET, BQ_TABLE,
    API_ENDPOINT, WRITE_MODE,
)

logger = get_logger(__name__)


def fetch_vehicles() -> list:
    """
    Fetches master vehicle data from Mock API.
    Returns full list of registered vehicles.
    """
    response = call_api_with_retry(
        base_url=get_mock_api_url(),
        endpoint=API_ENDPOINT,
    )

    results = response.get("results", [])

    for r in results:
        r["ingested_at"] = datetime.utcnow().isoformat()

    return results


def run_fetch():
    """
    Main entry point.
    Fetches vehicles master data and loads to BigQuery.
    Uses TRUNCATE since this is master data.
    Called by Airflow DAG task.
    """
    client = get_bq_client(GCP_PROJECT)
    rows   = fetch_vehicles()

    logger.info(f"Total vehicles fetched: {len(rows)}")

    load_to_bq(
        client=client,
        rows=rows,
        project=GCP_PROJECT,
        dataset=BQ_DATASET,
        table=BQ_TABLE,
        write_mode=WRITE_MODE,
    )

    logger.info("Vehicles ingestion complete!")


if __name__ == "__main__":
    run_fetch()