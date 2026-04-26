from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/ingestion')

from raw_vehicles.fetch import run_fetch as fetch_vehicles
from raw_vehicles.validate import run_validation as validate_vehicles
from raw_spare_parts.fetch import run_fetch as fetch_spare_parts
from raw_spare_parts.validate import run_validation as validate_spare_parts
from raw_service_orders.fetch import run_fetch as fetch_service_orders
from raw_service_orders.validate import run_validation as validate_service_orders
from raw_service_order_items.fetch import run_fetch as fetch_service_order_items
from raw_service_order_items.validate import run_validation as validate_service_order_items
from raw_sales_orders.fetch import run_fetch as fetch_sales_orders
from raw_sales_orders.validate import run_validation as validate_sales_orders
from raw_warranty_claims.fetch import run_fetch as fetch_warranty_claims
from raw_warranty_claims.validate import run_validation as validate_warranty_claims

default_args = {
    'owner': 'Ferdian',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'depends_on_past': False,
}

with DAG(
    dag_id='raw_auto_dummy_api_dag',
    default_args=default_args,
    description='Daily ingestion of automotive aftersales and sales data into BigQuery',
    schedule_interval='0 18 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['batch', 'automotive', 'aftersales', 'sales', 'daily'],
) as dag:

    # ── Master Data ──────────────────────────────────────────
    task_fetch_vehicles = PythonOperator(
        task_id='fetch_vehicles',
        python_callable=fetch_vehicles,
    )
    task_validate_vehicles = PythonOperator(
        task_id='validate_vehicles',
        python_callable=validate_vehicles,
    )

    task_fetch_spare_parts = PythonOperator(
        task_id='fetch_spare_parts',
        python_callable=fetch_spare_parts,
    )
    task_validate_spare_parts = PythonOperator(
        task_id='validate_spare_parts',
        python_callable=validate_spare_parts,
    )

    # ── Transactions ─────────────────────────────────────────
    task_fetch_service_orders = PythonOperator(
        task_id='fetch_service_orders',
        python_callable=fetch_service_orders,
    )
    task_validate_service_orders = PythonOperator(
        task_id='validate_service_orders',
        python_callable=validate_service_orders,
    )

    task_fetch_service_order_items = PythonOperator(
        task_id='fetch_service_order_items',
        python_callable=fetch_service_order_items,
    )
    task_validate_service_order_items = PythonOperator(
        task_id='validate_service_order_items',
        python_callable=validate_service_order_items,
    )

    task_fetch_sales_orders = PythonOperator(
        task_id='fetch_sales_orders',
        python_callable=fetch_sales_orders,
    )
    task_validate_sales_orders = PythonOperator(
        task_id='validate_sales_orders',
        python_callable=validate_sales_orders,
    )

    task_fetch_warranty_claims = PythonOperator(
        task_id='fetch_warranty_claims',
        python_callable=fetch_warranty_claims,
    )
    task_validate_warranty_claims = PythonOperator(
        task_id='validate_warranty_claims',
        python_callable=validate_warranty_claims,
    )

    # ── Dependencies ─────────────────────────────────────────

    # Master data runs in parallel first
    task_fetch_vehicles    >> task_validate_vehicles
    task_fetch_spare_parts >> task_validate_spare_parts

    # All transactions wait for master data to complete
    master_done = [task_validate_vehicles, task_validate_spare_parts]

    # Service orders → items (sequential — items depend on orders)
    master_done >> task_fetch_service_orders
    task_fetch_service_orders    >> task_validate_service_orders
    task_validate_service_orders >> task_fetch_service_order_items
    task_fetch_service_order_items >> task_validate_service_order_items

    # Sales and warranty run in parallel after master data
    master_done >> task_fetch_sales_orders
    master_done >> task_fetch_warranty_claims

    task_fetch_sales_orders    >> task_validate_sales_orders
    task_fetch_warranty_claims >> task_validate_warranty_claims