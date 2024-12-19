import json
import boto3
import urllib3
import datetime

## Firehose name need to be filled in.
FIREHOSE_NAME = <<firehose name>>

# List of cities with latitude and longitude
CITIES = [
    {"city": "Berlin", "latitude": 52.52, "longitude": 13.41},
    {"city": "New York", "latitude": 40.71, "longitude": -74.01},
    {"city": "Tokyo", "latitude": 35.68, "longitude": 139.76},
    {"city": "Sydney", "latitude": -33.87, "longitude": 151.21},
    {"city": "São Paulo", "latitude": -23.55, "longitude": -46.63},
]

# The lambda_handler function is invoked by AWS Lambda. The invocation occurs in response to the configured event, AWS EventBridge (CloudWatch Events)
def lambda_handler(event, context):
    http = urllib3.PoolManager()

    # Dynamic date range (last 6 months)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=180)

    records = []  # List to store final records
    fh = boto3.client('firehose')
    batch_size = 500

    for location in CITIES:
        city_name = location['city']
        latitude = location['latitude']
        longitude = location['longitude']

        # Open-Meteo API URL for specific city
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={latitude}&longitude={longitude}&hourly=temperature_2m"
               f"&timezone=UTC&start_date={start_date}&end_date={end_date}")

        # HTT RequestP
        r = http.request("GET", url)
        r_dict = json.loads(r.data.decode('utf-8')) # Convert JSON string to Python dictionary

        # Diagnostic log
        print(f"API response for {city_name}:", r_dict)

        # Data processing
        time_list = r_dict.get('hourly', {}).get('time', [])
        temp_list = r_dict.get('hourly', {}).get('temperature_2m', [])

        for time, temp in zip(time_list, temp_list):
            if temp is not None:
                processed_dict = {
                    'city': city_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'datetime': time,
                    'temperature': temp,
                    'row_ts': str(datetime.datetime.now()) # Adds a timestamp (exact date and time) of the script execution
                }
                record = {'Data': json.dumps(processed_dict) + '\n'}
                records.append(record)

                # Send in batches of 500 records
                if len(records) >= batch_size:
                    send_to_firehose(fh, records)
                    records = []  # Clean the batch after sending

    # Submit remaining records
    if records:
        send_to_firehose(fh, records)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Data from all cities processed successfully'})
    }

def send_to_firehose(client, records):
    response = client.put_record_batch(
        DeliveryStreamName=FIREHOSE_NAME,
        Records=records
    )
    print("Batch sent, Response:", response)
