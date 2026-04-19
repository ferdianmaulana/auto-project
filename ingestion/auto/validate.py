import logging
from google.cloud import bigquery
from config import BIGQUERY_PROJECT, BIGQUERY_DATASET_RAW

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = bigquery.Client(project=BIGQUERY_PROJECT)


def validate_table(table_name, checks):
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET_RAW}.{table_name}"
    errors = []

    for check_name, query in checks.items():
        full_query = query.replace("{table}", table_id)
        result = client.query(full_query).result()
        rows = list(result)

        if rows[0][0] > 0:
            errors.append(f"❌ {check_name}: {rows[0][0]} violations found")
        else:
            logger.info(f"✅ {check_name}: passed")

    if errors:
        raise ValueError(f"Data quality checks failed for {table_name}:\n" + "\n".join(errors))


def validate_complaints():
    validate_table("raw_complaints", {
        "null_make": "SELECT COUNT(*) FROM `{table}` WHERE make IS NULL",
        "null_model": "SELECT COUNT(*) FROM `{table}` WHERE model IS NULL",
        "null_modelYear": "SELECT COUNT(*) FROM `{table}` WHERE modelYear IS NULL",
        "invalid_year": "SELECT COUNT(*) FROM `{table}` WHERE modelYear < 2015 OR modelYear > 2024",
    })


def validate_recalls():
    validate_table("raw_recalls", {
        "null_make": "SELECT COUNT(*) FROM `{table}` WHERE make IS NULL",
        "null_model": "SELECT COUNT(*) FROM `{table}` WHERE model IS NULL",
        "null_modelYear": "SELECT COUNT(*) FROM `{table}` WHERE modelYear IS NULL",
    })


def validate_safety_ratings():
    validate_table("raw_safety_ratings", {
        "null_make": "SELECT COUNT(*) FROM `{table}` WHERE make IS NULL",
        "null_model": "SELECT COUNT(*) FROM `{table}` WHERE model IS NULL",
        "null_modelYear": "SELECT COUNT(*) FROM `{table}` WHERE modelYear IS NULL",
    })


def run_validation():
    logger.info("Running data quality checks...")
    validate_complaints()
    validate_recalls()
    validate_safety_ratings()
    logger.info("✅ All data quality checks passed!")


if __name__ == "__main__":
    run_validation()