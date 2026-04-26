import sys
sys.path.append('/opt/airflow/ingestion')

from datetime import datetime
from utils.dummy_api import call_api_with_retry, get_mock_api_url
from utils.bigquery import get_bq_client, load_to_bq
from utils.logger import get_logger
from raw_spare_parts.config import (
    GCP_PROJECT, BQ_DATASET, BQ_TABLE,
    API_ENDPOINT, WRITE_MODE,
)

logger = get_logger(__name__)


def fetch_spare_parts() -> list:
    response = call_api_with_retry(
        base_url=get_mock_api_url(),
        endpoint=API_ENDPOINT,
    )

    results = response.get("results", [])
    for r in results:
        r["ingested_at"] = datetime.utcnow().isoformat()

    return results


def run_fetch():
    client = get_bq_client(GCP_PROJECT)
    rows   = fetch_spare_parts()

    logger.info(f"Total spare parts fetched: {len(rows)}")

    load_to_bq(
        client=client,
        rows=rows,
        project=GCP_PROJECT,
        dataset=BQ_DATASET,
        table=BQ_TABLE,
        write_mode=WRITE_MODE,
    )

    logger.info("✅ Spare parts ingestion complete!")


if __name__ == "__main__":
    run_fetch()