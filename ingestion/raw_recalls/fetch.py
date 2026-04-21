import sys
sys.path.append('/opt/airflow/ingestion')

from datetime import datetime
from utils.api import call_api_with_retry, build_combinations
from utils.bigquery import get_bq_client, load_to_bq
from utils.logger import get_logger
from raw_recalls.config import (
    GCP_PROJECT, BQ_DATASET, BQ_TABLE,
    BASE_URL, API_ENDPOINT,
    VEHICLE_SCOPE, MODEL_YEARS, WRITE_MODE,
)

logger = get_logger(__name__)


def fetch_recalls(make: str, model: str, year: int) -> list:
    """
    Fetches recalls for a single make/model/year combination
    from the NHTSA API.
    """
    response = call_api_with_retry(
        base_url=BASE_URL,
        endpoint=API_ENDPOINT,
        params={"make": make, "model": model, "modelYear": year},
    )

    results = response.get("results", [])

    for r in results:
        r["make"] = make
        r["model"] = model
        r["modelYear"] = year
        r["ingested_at"] = datetime.utcnow().isoformat()

    return results


def run_fetch():
    """
    Main entry point.
    Fetches all recalls for all vehicle combinations
    and loads them into BigQuery.
    Called by Airflow DAG task.
    """
    client = get_bq_client(GCP_PROJECT)
    combinations = build_combinations(VEHICLE_SCOPE, MODEL_YEARS)
    total = len(combinations)
    all_rows = []

    for i, (make, model, year) in enumerate(combinations, 1):
        logger.info(f"[{i}/{total}] Fetching recalls: {make} {model} {year}")
        rows = fetch_recalls(make, model, year)
        all_rows.extend(rows)

    logger.info(f"Total recalls fetched: {len(all_rows)}")

    load_to_bq(
        client=client,
        rows=all_rows,
        project=GCP_PROJECT,
        dataset=BQ_DATASET,
        table=BQ_TABLE,
        write_mode=WRITE_MODE,
    )

    logger.info("Recalls ingestion complete!")


if __name__ == "__main__":
    run_fetch()