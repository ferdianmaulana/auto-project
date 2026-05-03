from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import DagRunState
from datetime import datetime, timedelta

from utils.callbacks import slack_failure_callback

DBT_PROJECT_DIR  = "/opt/airflow/dbt/auto_project"
DBT_PROFILES_DIR = "/opt/airflow/dbt/auto_project"

default_args = {
    'owner': 'Ferdian',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'depends_on_past': False,
    'on_failure_callback': slack_failure_callback,
}


def dbt_run(model: str) -> str:
    """Returns bash command to run a single dbt model."""
    return f"""
        cd {DBT_PROJECT_DIR} &&
        dbt run --select {model} --profiles-dir {DBT_PROFILES_DIR}
    """


def dbt_test(model: str) -> str:
    """Returns bash command to test a single dbt model."""
    return f"""
        cd {DBT_PROJECT_DIR} &&
        dbt test --select {model} --profiles-dir {DBT_PROFILES_DIR}
    """


with DAG(
    dag_id='transform_auto_dbt_dag',
    default_args=default_args,
    description='dbt transformations for automotive aftersales and sales data',
    schedule_interval='30 1 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['dbt', 'automotive', 'transformation', 'daily'],
) as dag:

    # ── Wait for ingestion DAG ───────────────────────────────
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

    # ── Setup ────────────────────────────────────────────────
    dbt_debug = BashOperator(
        task_id='dbt_debug',
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt debug --profiles-dir {DBT_PROFILES_DIR}",
    )

    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt deps --profiles-dir {DBT_PROFILES_DIR}",
    )

    # ── Staging models ───────────────────────────────────────
    run_stg_vehicles = BashOperator(
        task_id='run_stg_vehicles',
        bash_command=dbt_run('stg_vehicles'),
    )
    test_stg_vehicles = BashOperator(
        task_id='test_stg_vehicles',
        bash_command=dbt_test('stg_vehicles'),
    )

    run_stg_spare_parts = BashOperator(
        task_id='run_stg_spare_parts',
        bash_command=dbt_run('stg_spare_parts'),
    )
    test_stg_spare_parts = BashOperator(
        task_id='test_stg_spare_parts',
        bash_command=dbt_test('stg_spare_parts'),
    )

    run_stg_service_orders = BashOperator(
        task_id='run_stg_service_orders',
        bash_command=dbt_run('stg_service_orders'),
    )
    test_stg_service_orders = BashOperator(
        task_id='test_stg_service_orders',
        bash_command=dbt_test('stg_service_orders'),
    )

    run_stg_service_order_items = BashOperator(
        task_id='run_stg_service_order_items',
        bash_command=dbt_run('stg_service_order_items'),
    )
    test_stg_service_order_items = BashOperator(
        task_id='test_stg_service_order_items',
        bash_command=dbt_test('stg_service_order_items'),
    )

    run_stg_sales_orders = BashOperator(
        task_id='run_stg_sales_orders',
        bash_command=dbt_run('stg_sales_orders'),
    )
    test_stg_sales_orders = BashOperator(
        task_id='test_stg_sales_orders',
        bash_command=dbt_test('stg_sales_orders'),
    )

    run_stg_warranty_claims = BashOperator(
        task_id='run_stg_warranty_claims',
        bash_command=dbt_run('stg_warranty_claims'),
    )
    test_stg_warranty_claims = BashOperator(
        task_id='test_stg_warranty_claims',
        bash_command=dbt_test('stg_warranty_claims'),
    )

    # ── Consumption — dimensions ─────────────────────────────
    run_dim_vehicles = BashOperator(
        task_id='run_dim_vehicles',
        bash_command=dbt_run('dim_vehicles'),
    )
    test_dim_vehicles = BashOperator(
        task_id='test_dim_vehicles',
        bash_command=dbt_test('dim_vehicles'),
    )

    run_dim_dealers = BashOperator(
        task_id='run_dim_dealers',
        bash_command=dbt_run('dim_dealers'),
    )
    test_dim_dealers = BashOperator(
        task_id='test_dim_dealers',
        bash_command=dbt_test('dim_dealers'),
    )

    # ── Consumption — facts ──────────────────────────────────
    run_fct_service_orders = BashOperator(
        task_id='run_fct_service_orders',
        bash_command=dbt_run('fct_service_orders'),
    )
    test_fct_service_orders = BashOperator(
        task_id='test_fct_service_orders',
        bash_command=dbt_test('fct_service_orders'),
    )

    run_fct_sales_orders = BashOperator(
        task_id='run_fct_sales_orders',
        bash_command=dbt_run('fct_sales_orders'),
    )
    test_fct_sales_orders = BashOperator(
        task_id='test_fct_sales_orders',
        bash_command=dbt_test('fct_sales_orders'),
    )

    run_fct_warranty_claims = BashOperator(
        task_id='run_fct_warranty_claims',
        bash_command=dbt_run('fct_warranty_claims'),
    )
    test_fct_warranty_claims = BashOperator(
        task_id='test_fct_warranty_claims',
        bash_command=dbt_test('fct_warranty_claims'),
    )

    # ── Consumption — marts ──────────────────────────────────
    run_mart_dealer_performance = BashOperator(
        task_id='run_mart_dealer_performance',
        bash_command=dbt_run('mart_dealer_performance'),
    )
    test_mart_dealer_performance = BashOperator(
        task_id='test_mart_dealer_performance',
        bash_command=dbt_test('mart_dealer_performance'),
    )

    run_mart_brand_performance = BashOperator(
        task_id='run_mart_brand_performance',
        bash_command=dbt_run('mart_brand_performance'),
    )
    test_mart_brand_performance = BashOperator(
        task_id='test_mart_brand_performance',
        bash_command=dbt_test('mart_brand_performance'),
    )

    # ── Docs ─────────────────────────────────────────────────
    dbt_docs_generate = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt docs generate --profiles-dir {DBT_PROFILES_DIR}",
    )

    # ── Dependencies ─────────────────────────────────────────

    # Setup
    wait_for_ingestion >> dbt_debug >> dbt_deps

    # Staging — all run in parallel after setup
    dbt_deps >> run_stg_vehicles >> test_stg_vehicles
    dbt_deps >> run_stg_spare_parts >> test_stg_spare_parts
    dbt_deps >> run_stg_service_orders >> test_stg_service_orders
    dbt_deps >> run_stg_service_order_items >> test_stg_service_order_items
    dbt_deps >> run_stg_sales_orders >> test_stg_sales_orders
    dbt_deps >> run_stg_warranty_claims >> test_stg_warranty_claims

    # service_order_items depends on service_orders
    test_stg_service_orders >> run_stg_service_order_items

    # Dimensions — depend on their source staging models
    [test_stg_vehicles] >> run_dim_vehicles >> test_dim_vehicles
    [test_stg_service_orders,
     test_stg_sales_orders] >> run_dim_dealers >> test_dim_dealers

    # Facts — depend on dimensions
    [test_dim_vehicles,
     test_dim_dealers,
     test_stg_service_order_items] >> run_fct_service_orders >> test_fct_service_orders

    [test_dim_vehicles,
     test_dim_dealers,
     test_stg_sales_orders] >> run_fct_sales_orders >> test_fct_sales_orders

    [test_dim_vehicles,
     test_dim_dealers,
     test_stg_warranty_claims]>> run_fct_warranty_claims >> test_fct_warranty_claims

    # Marts — depend on all facts
    [test_fct_service_orders,
     test_fct_sales_orders,
     test_fct_warranty_claims] >> run_mart_dealer_performance >> test_mart_dealer_performance

    [test_fct_service_orders,
     test_fct_sales_orders,
     test_fct_warranty_claims] >> run_mart_brand_performance  >> test_mart_brand_performance

    # Docs — runs after all marts complete
    [test_mart_dealer_performance,
     test_mart_brand_performance] >> dbt_docs_generate