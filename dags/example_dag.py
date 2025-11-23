from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def _hello():
    print("Hello from the demo DAG inside the Airflow container!")


with DAG(
    dag_id="hello_demo",
    start_date=datetime(2025, 11, 23),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "team --build"},
) as dag:
    PythonOperator(task_id="say_hello", python_callable=_hello)
