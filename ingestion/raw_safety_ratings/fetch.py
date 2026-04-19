import sys
sys.path.append('/opt/airflow/ingestion')

from datetime import datetime
from utils.api import call_api_with_retry, build_combinations
from utils.bigquery import get_bq_client, load_to_bq
from utils.logger import get_logger
from raw_safety_ratings.config import (
    GCP_PROJECT, BQ_DATASET, BQ_TABLE,
    NHTSA_BASE_URL, API_ENDPOINT_TEMPLATE,
    VEHICLE_SCOPE, MODEL_YEARS, WRITE_MODE,
)

logger = get_logger(__name__)


def fetch_safety_ratings(make: str, model: str, year: int) -> list:
    """
    Fetches safety ratings for a single make/model/year combination
    from the NHTSA API.
    Note: Safety ratings uses path parameters instead of query parameters.
    """
    endpoint = API_ENDPOINT_TEMPLATE.format(
        year=year,
        make=make,
        model=model,
    )

    response = call_api_with_retry(
        base_url=NHTSA_BASE_URL,
        endpoint=endpoint,
    )

    results = response.get("Results", [])

    for r in results:
        r["make"] = make
        r["model"] = model
        r["modelYear"] = year
        r["ingested_at"] = datetime.utcnow().isoformat()

    return results


def run_fetch():
    """
    Main entry point.
    Fetches all safety ratings for all vehicle combinations
    and loads them into BigQuery.
    Called by Airflow DAG task.
    """
    client = get_bq_client(GCP_PROJECT)
    combinations = build_combinations(VEHICLE_SCOPE, MODEL_YEARS)
    total = len(combinations)
    all_rows = []

    for i, (make, model, year) in enumerate(combinations, 1):
        logger.info(f"[{i}/{total}] Fetching safety ratings: {make} {model} {year}")
        rows = fetch_safety_ratings(make, model, year)
        all_rows.extend(rows)

    logger.info(f"Total safety ratings fetched: {len(all_rows)}")

    load_to_bq(
        client=client,
        rows=all_rows,
        project=GCP_PROJECT,
        dataset=BQ_DATASET,
        table=BQ_TABLE,
        write_mode=WRITE_MODE,
    )

    logger.info("Safety ratings ingestion complete!")


if __name__ == "__main__":
    run_fetch()