from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/ingestion/auto')

from fetch import run_ingestion
from validate import run_validation

default_args = {
    'owner': 'your_name',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

with DAG(
    dag_id='raw_auto_use_case_dag',
    default_args=default_args,
    description='Ingest automotive complaints, recalls, and safety ratings into BigQuery',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['batch', 'nhtsa', 'automotive'],
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_auto_data',
        python_callable=run_ingestion,
    )

    validate_task = PythonOperator(
        task_id='validate_raw_data',
        python_callable=run_validation,
    )

    ingest_task >> validate_task