from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/ingestion')

from raw_complaints.fetch import run_fetch as fetch_complaints
from raw_complaints.validate import run_validation as validate_complaints
from raw_recalls.fetch import run_fetch as fetch_recalls
from raw_recalls.validate import run_validation as validate_recalls
from raw_safety_ratings.fetch import run_fetch as fetch_safety_ratings
from raw_safety_ratings.validate import run_validation as validate_safety_ratings

default_args = {
    'owner': 'your_name',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'depends_on_past': False,
}

with DAG(
    dag_id='raw_auto_use_case_dag',
    default_args=default_args,
    description='Weekly ingestion of NHTSA complaints, recalls and safety ratings into BigQuery',
    schedule_interval='@weekly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['batch', 'nhtsa', 'automotive', 'weekly'],
) as dag:

    # ── Complaints ──────────────────────────────────────────
    task_fetch_complaints = PythonOperator(
        task_id='fetch_complaints',
        python_callable=fetch_complaints,
    )

    task_validate_complaints = PythonOperator(
        task_id='validate_complaints',
        python_callable=validate_complaints,
    )

    # ── Recalls ─────────────────────────────────────────────
    task_fetch_recalls = PythonOperator(
        task_id='fetch_recalls',
        python_callable=fetch_recalls,
    )

    task_validate_recalls = PythonOperator(
        task_id='validate_recalls',
        python_callable=validate_recalls,
    )

    # ── Safety Ratings ───────────────────────────────────────
    task_fetch_safety_ratings = PythonOperator(
        task_id='fetch_safety_ratings',
        python_callable=fetch_safety_ratings,
    )

    task_validate_safety_ratings = PythonOperator(
        task_id='validate_safety_ratings',
        python_callable=validate_safety_ratings,
    )

    # ── Task Dependencies ────────────────────────────────────
    task_fetch_complaints >> task_validate_complaints
    task_fetch_recalls >> task_validate_recalls
    task_fetch_safety_ratings >> task_validate_safety_ratings