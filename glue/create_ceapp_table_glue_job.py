import sys
import boto3

client = boto3.client('athena')

SOURCE_TABLE_NAME = 'weather_data_bucket_project_2024'
NEW_TABLE_NAME = 'open_meteo_weather_data_parquet_tbl'
NEW_TABLE_S3_BUCKET = 's3://open-meteo-weather-data-parquet/'
MY_DATABASE = 'proj_database'
QUERY_RESULTS_S3_BUCKET = 's3://athena-query-results-location-proj'

# Refresh the table
queryStart = client.start_query_execution(
    QueryString = f"""
    CREATE TABLE {NEW_TABLE_NAME} WITH
    (external_location='{NEW_TABLE_S3_BUCKET}',
    format='PARQUET',
    write_compression='SNAPPY',
    partitioned_by = ARRAY['yr_mo_partition'])
    AS

    SELECT
        'Berlin' as City
        ,'Germany' as Country
        ,SPLIT(datetime, 'T')[1] AS Date 
        ,SPLIT(datetime, 'T')[2] AS Time
        ,Temperature  
        ,row_ts as "Processing Time"
        ,CONCAT(SUBSTR(datetime, 1, 4), '-', SUBSTR(datetime, 6, 2)) AS yr_mo_partition
    FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"

    ;
    """,
    QueryExecutionContext = {
        'Database': f'{MY_DATABASE}'
    }, 
    ResultConfiguration = { 'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET}'}
)

# list of responses
resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

# get the response
response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

# wait until query finishes
while response["QueryExecution"]["Status"]["State"] not in resp:
    response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])
    
# if it fails, exit and give the Athena error message in the logs
if response["QueryExecution"]["Status"]["State"] == 'FAILED':
    sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])
