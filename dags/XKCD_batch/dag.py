from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import requests
import json

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "retries": 1,
}

dag = DAG(
    "xkcd_batch_loader",
    default_args=default_args,
    description="A DAG to batch load XKCD data until the current num",
    schedule_interval=None,  # No schedule, triggered manually
)


def fetch_xkcd_data(backlog_startpoint):
    """
    Fetches XKCD data for a given comic number.

    :param backlog_startpoint: The comic number to fetch data for.
    :type backlog_startpoint: int
    :return: The fetched XKCD data.
    :rtype: dict
    """
    url = f"https://xkcd.com/{backlog_startpoint}/info.0.json"
    response = requests.get(url)
    try:
        data = response.json()
        print("Fetched XKCD Data:", data)  # Debugging line
    except json.JSONDecodeError:
        data = {}
    return data


def get_latest_num():
    """
    Retrieves the latest comic number from the database.

    :return: The latest comic number.
    :rtype: int
    """
    pg_hook = PostgresHook(postgres_conn_id="dwh_postgresql")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(num) FROM staging.comics")
    result = cursor.fetchone()
    latest_num = result[0] if result[0] else 0

    cursor.close()
    conn.close()

    return latest_num


def store_xkcd_data(**context):
    """
    Fetches and stores XKCD data in the database from the backlog start point to the latest comic number.

    :param context: Airflow context that provides runtime information.
    :type context: dict
    """
    backlog_startpoint = int(Variable.get("backlog_startpoint", default_var=1))
    latest_num = get_latest_num()

    pg_hook = PostgresHook(postgres_conn_id="dwh_postgresql")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    while backlog_startpoint <= latest_num:
        xkcd_data = fetch_xkcd_data(backlog_startpoint)

        cursor.execute(
            "SELECT 1 FROM staging.comics WHERE num = %s", (xkcd_data["num"],)
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                """
            INSERT INTO staging.comics (num, title, img, alt, year, month, day)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    xkcd_data["num"],
                    xkcd_data["title"],
                    xkcd_data["img"],
                    xkcd_data["alt"],
                    xkcd_data["year"],
                    xkcd_data["month"],
                    xkcd_data["day"],
                ),
            )

        backlog_startpoint += 1

    conn.commit()
    cursor.close()
    conn.close()


store_xkcd_data_task = PythonOperator(
    task_id="store_xkcd_data",
    python_callable=store_xkcd_data,
    provide_context=True,
    dag=dag,
)
