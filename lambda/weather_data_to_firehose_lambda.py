import json
import boto3
import urllib3
import datetime

## Firehose name need to be filled in.
FIREHOSE_NAME = <<firehose name>>

def lambda_handler(event, context):
    http = urllib3.PoolManager()
    
    # Open-Meteo API request
    url = ("https://api.open-meteo.com/v1/forecast"
           "?latitude=52.52&longitude=13.41&daily=temperature_2m_max,temperature_2m_min"
           "&timezone=America%2FLos_Angeles&start_date=2024-06-01&end_date=2024-11-30")
    
    r = http.request("GET", url)
    r_dict = json.loads(r.data.decode(encoding='utf-8', errors='strict'))
    
    # Process daily temperatures
    processed_data = []
    for i in range(len(r_dict['daily']['time'])):
        record = {
            'date': r_dict['daily']['time'][i],
            'temperature_max': r_dict['daily']['temperature_2m_max'][i],
            'temperature_min': r_dict['daily']['temperature_2m_min'][i],
            'row_ts': str(datetime.datetime.now())
        }
        processed_data.append(record)
    
    # Send each record to the Firehose
    fh = boto3.client('firehose')
    for record in processed_data:
        msg = json.dumps(record) + '\n'
        fh.put_record(
            DeliveryStreamName=FIREHOSE_NAME,
            Record={'Data': msg}
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Daily temperatures sent to Firehose', 'records_sent': len(processed_data)})
    }
