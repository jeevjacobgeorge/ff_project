from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
import pandas as pd
from datetime import datetime

# Define constants
GCP_PROJECT_ID = "enhanced-cable-447317-h8"
BQ_DATASET = "ksrtc_dataset"
BQ_TABLE = "ksrtc_vis_view"
CSV_FILE_PATH = "/home/jeev/project/project_backend/ksrtc4/pred/data/airflow.csv"  # Change to your preferred local path

# BigQuery SQL Query
SQL_QUERY = f"""SELECT 
    CONCAT(TICKET_ISSUE_DATE, ' ', FORMAT_TIMESTAMP('%H', TIMESTAMP(CONCAT(TICKET_ISSUE_DATE, ' ', TICKET_ISSUE_TIME)))) AS DATE_HOUR,
    TO_STOP_NAME,
    SUM(TOTAL_PASSENGER) AS TOTAL_PASSENGER
FROM `enhanced-cable-447317-h8.ksrtc_dataset.ksrtc_tablef`
GROUP BY DATE_HOUR, TO_STOP_NAME
ORDER BY DATE_HOUR;
"""

def save_bigquery_data_to_csv():
    """Fetch data from BigQuery and save as CSV."""
    client = bigquery.Client()
    df = client.query(SQL_QUERY).to_dataframe()  # Get data as DataFrame
    
    # Check if DataFrame is empty
    if df.empty:
        print("No data fetched from BigQuery!")
    else:
        print(f"Fetched {len(df)} rows from BigQuery")
    
    df.to_csv(CSV_FILE_PATH, index=False)  # Save as CSV (overwrite existing file)
    print(f"CSV saved to {CSV_FILE_PATH}")

# Define DAG
default_args = {
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="pred_to",
    default_args=default_args,
    schedule="00 02 * * *",  # Run daily at 11:59 AM
    catchup=False,
) as dag:
    # Step 1: Execute BigQuery Query
    run_query = BigQueryInsertJobOperator(
        task_id="run_query",
        configuration={
            "query": {
                "query": SQL_QUERY,
                "useLegacySql": False,
            }
        },
        gcp_conn_id="google_cloud_default"  # Make sure this is configured in Airflow connections
    )

    # Step 2: Save Data to CSV
    save_csv = PythonOperator(
        task_id="save_csv",
        python_callable=save_bigquery_data_to_csv
    )

    run_query >> save_csv  # Task dependencies
