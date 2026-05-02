from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

DBT_PROJECT_DIR = "/opt/airflow/dbt/auto_project"
DBT_PROFILES_DIR = "/opt/airflow/dbt/auto_project"

default_args = {
    'owner':            'Ferdian',
    'retries':          1,
    'retry_delay':      timedelta(minutes=5),
    'email_on_failure': False,
    'depends_on_past':  False,
}

with DAG(
    dag_id='transform_auto_dbt_dag',
    default_args=default_args,
    description='dbt transformations for automotive aftersales and sales data',
    schedule_interval='30 1 * * *',  # 02:00 WIB — 1 hour after ingestion
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['dbt', 'automotive', 'transformation', 'daily'],
) as dag:

    # ── Wait for ingestion DAG to complete ───────────────────
    wait_for_ingestion = ExternalTaskSensor(
        task_id='wait_for_ingestion',
        external_dag_id='raw_auto_dummy_api_dag',
        external_task_id=None,          # None = wait for entire DAG
        allowed_states=['success'],
        failed_states=['failed', 'upstream_failed'],
        execution_delta=timedelta(hours=1),  # ingestion runs 1 hour earlier
        timeout=3600,                   # wait max 1 hour
        poke_interval=60,               # check every 60 seconds
        mode='poke',
    )

    # ── dbt commands ─────────────────────────────────────────
    dbt_debug = BashOperator(
        task_id='dbt_debug',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt debug --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt deps --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_run_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt run --select staging --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_test_staging = BashOperator(
        task_id='dbt_test_staging',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt test --select staging --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_run_consumption = BashOperator(
        task_id='dbt_run_consumption',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt run --select consumption --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_test_consumption = BashOperator(
        task_id='dbt_test_consumption',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt test --select consumption --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_docs_generate = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=f"""
            cd {DBT_PROJECT_DIR} &&
            dbt docs generate --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    # ── Task Dependencies ────────────────────────────────────
    (
        wait_for_ingestion
        >> dbt_debug
        >> dbt_deps
        >> dbt_run_staging
        >> dbt_test_staging
        >> dbt_run_consumption
        >> dbt_test_consumption
        >> dbt_docs_generate
    )