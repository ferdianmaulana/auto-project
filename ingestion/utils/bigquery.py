from google.cloud import bigquery
from utils.logger import get_logger

logger = get_logger(__name__)


def get_bq_client(project: str) -> bigquery.Client:
    """
    Returns an authenticated BigQuery client.
    Works for any GCP project.

    Args:
        project: GCP project ID e.g. "de-portfolio-automotive"
    """
    return bigquery.Client(project=project)


def load_to_bq(
    client: bigquery.Client,
    rows: list,
    project: str,
    dataset: str,
    table: str,
    write_mode: str = "APPEND",
) -> None:
    """
    Loads a list of dicts into any BigQuery table.
    Schema is auto-detected from the data.

    Args:
        client:     BigQuery client
        rows:       List of dicts to load
        project:    GCP project ID
        dataset:    BigQuery dataset ID
        table:      BigQuery table ID
        write_mode: "APPEND", "TRUNCATE", or "EMPTY"
                    Defaults to APPEND for raw layer
    """
    if not rows:
        logger.info(f"No rows to load into {dataset}.{table} — skipping")
        return

    table_id = f"{project}.{dataset}.{table}"

    write_disposition_map = {
        "APPEND":   bigquery.WriteDisposition.WRITE_APPEND,
        "TRUNCATE": bigquery.WriteDisposition.WRITE_TRUNCATE,
        "EMPTY":    bigquery.WriteDisposition.WRITE_EMPTY,
    }

    write_disposition = write_disposition_map.get(
        write_mode.upper(),
        bigquery.WriteDisposition.WRITE_APPEND
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=True,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()

    logger.info(f"Loaded {len(rows)} rows into {table_id} (mode: {write_mode})")


def run_bq_query(
    client: bigquery.Client,
    query: str,
) -> list:
    """
    Runs any SQL query on BigQuery and returns results as a list of rows.
    Can be used for validation, lookups, or any ad-hoc query.

    Args:
        client: BigQuery client
        query:  SQL query string

    Returns:
        List of BigQuery Row objects
    """
    result = client.query(query).result()
    return list(result)


def validate_bq_check(
    client: bigquery.Client,
    check_name: str,
    query: str,
) -> bool:
    """
    Runs a data quality check query against BigQuery.
    The query must return a single integer — 0 means pass, >0 means fail.

    Can be used to validate any table in any dataset.

    Args:
        client:     BigQuery client
        check_name: Human-readable name for the check
        query:      SQL that returns a single count of violations

    Returns:
        True if check passes (0 violations), False otherwise

    Example query:
        "SELECT COUNT(*) FROM `project.dataset.table` WHERE column IS NULL"
    """
    rows = run_bq_query(client, query)
    count = rows[0][0]

    if count > 0:
        logger.error(f"{check_name}: {count} violations found")
        return False

    logger.info(f"{check_name}: passed")
    return True


def table_exists(
    client: bigquery.Client,
    project: str,
    dataset: str,
    table: str,
) -> bool:
    """
    Checks if a BigQuery table exists.
    Useful before running validations on a fresh setup.

    Args:
        client:  BigQuery client
        project: GCP project ID
        dataset: BigQuery dataset ID
        table:   BigQuery table ID

    Returns:
        True if table exists, False otherwise
    """
    table_id = f"{project}.{dataset}.{table}"
    try:
        client.get_table(table_id)
        return True
    except Exception:
        return False


def get_row_count(
    client: bigquery.Client,
    project: str,
    dataset: str,
    table: str,
) -> int:
    """
    Returns the total row count of any BigQuery table.

    Args:
        client:  BigQuery client
        project: GCP project ID
        dataset: BigQuery dataset ID
        table:   BigQuery table ID

    Returns:
        Row count as integer
    """
    table_id = f"{project}.{dataset}.{table}"
    query = f"SELECT COUNT(*) FROM `{table_id}`"
    rows = run_bq_query(client, query)
    return rows[0][0]