import sys
sys.path.append('/opt/airflow/ingestion')

from datetime import datetime, date
from utils.dummy_api import call_api_with_retry, get_dummy_api_url
from utils.bigquery import get_bq_client, load_to_bq
from utils.logger import get_logger
from raw_warranty_claims.config import (
    GCP_PROJECT, BQ_DATASET, BQ_TABLE,
    API_ENDPOINT, WRITE_MODE,
)

logger = get_logger(__name__)


def fetch_warranty_claims(target_date: date = None) -> list:
    target_date = target_date or date.today()

    response = call_api_with_retry(
        base_url=get_dummy_api_url(),
        endpoint=API_ENDPOINT,
        params={"date": str(target_date)},
    )

    results = response.get("results", [])
    for r in results:
        r["ingested_at"] = datetime.utcnow().isoformat()

    return results


def run_fetch():
    client      = get_bq_client(GCP_PROJECT)
    target_date = date.today()
    rows        = fetch_warranty_claims(target_date)

    logger.info(f"Total warranty claims fetched for {target_date}: {len(rows)}")

    load_to_bq(
        client=client,
        rows=rows,
        project=GCP_PROJECT,
        dataset=BQ_DATASET,
        table=BQ_TABLE,
        write_mode=WRITE_MODE,
    )

    logger.info("✅ Warranty claims ingestion complete!")


if __name__ == "__main__":
    run_fetch()