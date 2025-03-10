from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.dates import days_ago
from airflow.utils.decorators import apply_defaults
import requests
import json

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "retries": 1,
}

dag = DAG(
    "xkcd_daily",
    default_args=default_args,
    description="A simple DAG to fetch XKCD data and store in DWH",
    schedule_interval="0 0 * * 1,3,5",  # Runs on Monday, Wednesday, and Friday
)


def fetch_xkcd_data():
    """
    Fetch the latest XKCD comic data from the XKCD API.

    Returns:
        dict: The JSON response from the XKCD API containing comic data.
    """
    conn_id = "xkcd_api"
    connection = BaseHook.get_connection(conn_id)
    url = connection.host
    response = requests.get(url)
    try:
        data = response.json()
        print("Fetched XKCD Data:", data)  # Debugging line
    except json.JSONDecodeError:
        data = {}
    return data


def check_xkcd_data(xkcd_data):
    """
    Check if the fetched XKCD comic data is new by comparing with the latest comic number in the database.

    Args:
        xkcd_data (dict): The fetched XKCD comic data.

    Returns:
        bool: True if the fetched comic number is greater than the latest comic number in the database, False otherwise.
    """
    xkcd_num = xkcd_data["num"]

    pg_hook = PostgresHook(postgres_conn_id="dwh_postgresql")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(num) FROM staging.comics")
    result = cursor.fetchone()
    latest_num = result[0] if result[0] else 0

    cursor.close()
    conn.close()

    return xkcd_num > latest_num


def store_xkcd_data(**context):
    """
    Store the fetched XKCD comic data into the database if it is new.

    Args:
        context (dict): The context dictionary containing task instance information.
    """
    xkcd_data = context["task_instance"].xcom_pull(task_ids="fetch_xkcd_data")

    pg_hook = PostgresHook(postgres_conn_id="dwh_postgresql")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT num FROM staging.comics WHERE num = %s", (xkcd_data["num"],))
    result = cursor.fetchone()

    # Make sure only to add new values (add idempotency)
    if not result:
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
        conn.commit()

    cursor.close()
    conn.close()


class XKCDDataSensor(BaseSensorOperator):
    """
    Sensor to check if the fetched XKCD comic data is new and push it to XCom if it is.
    """

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super(XKCDDataSensor, self).__init__(*args, **kwargs)

    def poke(self, context):
        """
        Check if the fetched XKCD comic data is new.

        Args:
            context (dict): The context dictionary containing task instance information.

        Returns:
            bool: True if the fetched comic data is new, False otherwise.
        """
        xkcd_data = fetch_xkcd_data()
        if check_xkcd_data(xkcd_data):
            context["task_instance"].xcom_push(key="xkcd_data", value=xkcd_data)
            return True
        return False


fetch_xkcd_data_task = PythonOperator(
    task_id="fetch_xkcd_data",
    python_callable=fetch_xkcd_data,
    dag=dag,
)

xkcd_data_sensor_task = XKCDDataSensor(
    task_id="xkcd_data_sensor",
    poke_interval=600,  # Retry every 10 minutes
    timeout=60 * 60 * 24,  # Timeout after 24 hours
    dag=dag,
)

store_xkcd_data_task = PythonOperator(
    task_id="store_xkcd_data",
    python_callable=store_xkcd_data,
    provide_context=True,
    dag=dag,
)

fetch_xkcd_data_task >> xkcd_data_sensor_task >> store_xkcd_data_task
