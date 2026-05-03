from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import DagRunState

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.constants import ExecutionMode

DBT_PROJECT_DIR = Path("/opt/airflow/dbt/auto_project")

default_args = {
    'owner':            'Ferdian',
    'retries':          0,
    'retry_delay':      timedelta(minutes=5),
    'email_on_failure': False,
    'depends_on_past':  False,
}

project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_DIR,
)

profile_config = ProfileConfig(
    profile_name="auto_project",
    target_name="prod",
    profiles_yml_filepath=DBT_PROJECT_DIR / "profiles.yml",
)

execution_config = ExecutionConfig(
    execution_mode=ExecutionMode.LOCAL,
)

with DAG(
    dag_id='transform_auto_dbt_dag',
    default_args=default_args,
    description='dbt transformations for automotive aftersales and sales data',
    schedule_interval='30 1 * * *',  # 01:30 WIB — 30 mins after ingestion
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['dbt', 'automotive', 'transformation', 'daily'],
) as dag:

    # ── Wait for ingestion DAG ────────────────────────────────
    wait_for_ingestion = ExternalTaskSensor(
        task_id='wait_for_ingestion',
        external_dag_id='raw_auto_dummy_api_dag',
        external_task_id=None,
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        execution_delta=timedelta(minutes=30),
        timeout=3600,
        poke_interval=60,
        mode='poke',
    )

    # ── Install dbt packages ──────────────────────────────────
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt deps --profiles-dir {DBT_PROJECT_DIR}",
    )

    # ── Staging layer: one task per model (run + test) ────────
    staging = DbtTaskGroup(
        group_id='staging',
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=RenderConfig(select=['path:models/staging']),
    )

    # ── Consumption layer: one task per model (run + test) ────
    consumption = DbtTaskGroup(
        group_id='consumption',
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=RenderConfig(select=['path:models/consumption']),
    )

    # ── Generate docs (non-blocking, runs last) ───────────────
    dbt_docs_generate = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt docs generate --profiles-dir {DBT_PROJECT_DIR}",
    )

    # ── Pipeline ──────────────────────────────────────────────
    wait_for_ingestion >> dbt_deps >> staging >> consumption >> dbt_docs_generate
