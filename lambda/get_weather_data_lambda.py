import json
import boto3
import urllib3
import datetime

## Firehose name need to be filled in.
FIREHOSE_NAME = <<firehose name>>

def lambda_handler(event, context):
    http = urllib3.PoolManager()
    
    # Calculate dynamic dates (last 6 months)
    end_date = datetime.date.today()  # Today's date
    start_date = (end_date - datetime.timedelta(days=180))  # Go back 180 days (~6 months)

    # Open-Meteo API URL with dynamic dates
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude=52.52&longitude=13.41&hourly=temperature_2m"
           f"&timezone=America%2FLos_Angeles&start_date={start_date}&end_date={end_date}")

    # HTTP Request
    r = http.request("GET", url)
    r_dict = json.loads(r.data.decode('utf-8'))

    # Diagnostic log
    print("Resposta da API:", r_dict)

    # Lists of times and temperatures
    time_list = r_dict.get('hourly', {}).get('time', [])
    temp_list = r_dict.get('hourly', {}).get('temperature_2m', [])

    if not time_list or not temp_list:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Nenhum dado disponível'})
        }

    # Prepare valid records for Firehose
    records = []
    for time, temp in zip(time_list, temp_list):
        if temp is not None:
            processed_dict = {
                'latitude': r_dict['latitude'],
                'longitude': r_dict['longitude'],
                'datetime': time,  # Includes full date and time
                'temperature': temp,
                'row_ts': str(datetime.datetime.now())  # Insertion timestamp
            }
            record = {'Data': json.dumps(processed_dict) + '\n'}
            records.append(record)

    # Send in batches of up to 500 records
    fh = boto3.client('firehose')
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        response = fh.put_record_batch(
            DeliveryStreamName=FIREHOSE_NAME,
            Records=batch
        )
        print(f"Batch sent: {i//batch_size + 1}, Response: {response}")

    # Final answer
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Records sent successfully',
            'total_records': len(records),
            'batches_sent': (len(records) + batch_size - 1) // batch_size
        })
    }
