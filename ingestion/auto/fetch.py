import requests
import time
import logging
from datetime import datetime
from google.cloud import bigquery
from config import (
    VEHICLE_SCOPE,
    MODEL_YEARS,
    BASE_URL,
    BIGQUERY_PROJECT,
    BIGQUERY_DATASET_RAW,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = bigquery.Client(project=BIGQUERY_PROJECT)


def fetch_complaints(make, model, year):
    url = f"{BASE_URL}/complaints/complaintsByVehicle"
    params = {"make": make, "model": model, "modelYear": year}
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("results", [])
        for r in results:
            r["make"] = make
            r["model"] = model
            r["modelYear"] = year
            r["ingested_at"] = datetime.utcnow().isoformat()
        return results
    except Exception as e:
        logger.error(f"Failed complaints {make} {model} {year}: {e}")
        return []


def fetch_recalls(make, model, year):
    url = f"{BASE_URL}/recalls/recallsByVehicle"
    params = {"make": make, "model": model, "modelYear": year}
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("results", [])
        for r in results:
            r["make"] = make
            r["model"] = model
            r["modelYear"] = year
            r["ingested_at"] = datetime.utcnow().isoformat()
        return results
    except Exception as e:
        logger.error(f"Failed recalls {make} {model} {year}: {e}")
        return []


def fetch_safety_ratings(make, model, year):
    url = f"{BASE_URL}/SafetyRatings/modelyear/{year}/make/{make}/model/{model}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("Results", [])
        ratings = []
        for r in results:
            r["make"] = make
            r["model"] = model
            r["modelYear"] = year
            r["ingested_at"] = datetime.utcnow().isoformat()
            ratings.append(r)
        return ratings
    except Exception as e:
        logger.error(f"Failed safety ratings {make} {model} {year}: {e}")
        return []


def load_to_bigquery(rows, table_name):
    if not rows:
        logger.info(f"No rows to load for {table_name}")
        return

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET_RAW}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=True,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()
    logger.info(f"✅ Loaded {len(rows)} rows into {table_id}")


def run_ingestion():
    all_complaints = []
    all_recalls = []
    all_safety_ratings = []

    total = sum(len(models) for models in VEHICLE_SCOPE.values()) * len(MODEL_YEARS)
    counter = 0

    for make, models in VEHICLE_SCOPE.items():
        for model in models:
            for year in MODEL_YEARS:
                counter += 1
                logger.info(f"[{counter}/{total}] Fetching {make} {model} {year}...")

                complaints = fetch_complaints(make, model, year)
                all_complaints.extend(complaints)

                recalls = fetch_recalls(make, model, year)
                all_recalls.extend(recalls)

                ratings = fetch_safety_ratings(make, model, year)
                all_safety_ratings.extend(ratings)

                # Avoid hammering the API
                time.sleep(REQUEST_DELAY)

    logger.info(f"Total complaints: {len(all_complaints)}")
    logger.info(f"Total recalls: {len(all_recalls)}")
    logger.info(f"Total safety ratings: {len(all_safety_ratings)}")

    # Load to BigQuery
    load_to_bigquery(all_complaints, "raw_complaints")
    load_to_bigquery(all_recalls, "raw_recalls")
    load_to_bigquery(all_safety_ratings, "raw_safety_ratings")

    logger.info("✅ Ingestion complete!")


if __name__ == "__main__":
    run_ingestion()