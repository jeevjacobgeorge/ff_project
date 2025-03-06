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
CSV_FROM_PATH = "/home/jeev/project/project_backend/ksrtc3/passenger_distribution/data/caches/from_airflow.csv"
CSV_TO_PATH = "/home/jeev/project/project_backend/ksrtc3/passenger_distribution/data/caches/to_airflow.csv"

# BigQuery SQL Queries
SQL_FROM_QUERY = f"""SELECT 
    CONCAT(TICKET_ISSUE_DATE, ' ', FORMAT_TIMESTAMP('%H', TIMESTAMP(CONCAT(TICKET_ISSUE_DATE, ' ', TICKET_ISSUE_TIME)))) AS DATE_HOUR,
    FROM_STOP_NAME,
    SUM(TOTAL_PASSENGER) AS TOTAL_PASSENGER
FROM `enhanced-cable-447317-h8.ksrtc_dataset.ksrtc_tablef`
GROUP BY DATE_HOUR, FROM_STOP_NAME
ORDER BY DATE_HOUR;
"""

SQL_TO_QUERY = f"""SELECT 
    CONCAT(TICKET_ISSUE_DATE, ' ', FORMAT_TIMESTAMP('%H', TIMESTAMP(CONCAT(TICKET_ISSUE_DATE, ' ', TICKET_ISSUE_TIME)))) AS DATE_HOUR,
    TO_STOP_NAME,
    SUM(TOTAL_PASSENGER) AS TOTAL_PASSENGER
FROM `enhanced-cable-447317-h8.ksrtc_dataset.ksrtc_tablef`
GROUP BY DATE_HOUR, TO_STOP_NAME
ORDER BY DATE_HOUR;
"""

def save_bigquery_data_to_csv(query, file_path):
    """Fetch data from BigQuery and save as CSV."""
    client = bigquery.Client()
    df = client.query(query).to_dataframe()  # Get data as DataFrame
    
    if df.empty:
        print(f"No data fetched from BigQuery for {file_path}!")
    else:
        print(f"Fetched {len(df)} rows from BigQuery for {file_path}")
    
    df.to_csv(file_path, index=False)
    print(f"CSV saved to {file_path}")

# Define DAG
default_args = {
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="bigquery_to_csv_dual",
    default_args=default_args,
    schedule="00 10 * * *",  # Run daily at 11:59 AM
    catchup=False,
) as dag:
    # Step 1: Execute BigQuery Queries
    run_from_query = BigQueryInsertJobOperator(
        task_id="run_from_query",
        configuration={"query": {"query": SQL_FROM_QUERY, "useLegacySql": False}},
        gcp_conn_id="google_cloud_default"
    )
    
    run_to_query = BigQueryInsertJobOperator(
        task_id="run_to_query",
        configuration={"query": {"query": SQL_TO_QUERY, "useLegacySql": False}},
        gcp_conn_id="google_cloud_default"
    )

    # Step 2: Save Data to CSV
    save_from_csv = PythonOperator(
        task_id="save_from_csv",
        python_callable=save_bigquery_data_to_csv,
        op_args=[SQL_FROM_QUERY, CSV_FROM_PATH]
    )
    
    save_to_csv = PythonOperator(
        task_id="save_to_csv",
        python_callable=save_bigquery_data_to_csv,
        op_args=[SQL_TO_QUERY, CSV_TO_PATH]
    )

    # Define dependencies
    run_from_query >> save_from_csv
    run_to_query >> save_to_csv
