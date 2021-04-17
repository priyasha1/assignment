import json
import boto3
from datetime import datetime
from boto3 import resource
from botocore.exceptions import ClientError

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('dynamodb')
dynamodb_resource = resource('dynamodb')
tableName='customer_data'
table = dynamodb_resource.Table(tableName)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    password=event['key1']
    telephone=event['key2']
    
    if not all(password.isdigit(), len(password) == 6):
        return "Password should be 6 digit numeric"
    
    try:
        resp=table.update_item(
            Key={'telephone_number': event['key2']},
            UpdateExpression='SET password = :val1',
            ExpressionAttributeValues={':val1':password},
            ConditionExpression='attribute_exists(telephone_number)'
        )
        records = create_and_upload_record(password,telephone)
    except ClientError as e:  
        if e.response['Error']['Code']=='ConditionalCheckFailedException':  
            logger.info(e.response['Error'])
            return 'Record with provided phone number does not exists'
    
    
    resp=table.update_item(
            Key={'telephone_number': event['key2']
            },
            UpdateExpression='SET file_name=:val2, file_size=:val3, created_timestamp=:val4',
            ExpressionAttributeValues={
                ':val2':records['file_name'],
                ':val3':records['size'],
                ':val4':records['timestamp']},
            ConditionExpression='attribute_exists(telephone_number)',
            ReturnValues="UPDATED_NEW"
        )
    logger.info(resp)
    
def create_and_upload_record(password,telephone):
    bucket='customer-contact-data'
    key = '{}.txt'.format(telephone)
    
    s3_client.put_object(
        Body='{},{}'.format(password, telephone),
        Bucket=bucket,
        Key=key
    )
    
    data = s3_client.get_object(Bucket=bucket, Key=key)
    
    object_info = {
        'file_name': key,
        'size': data['ContentLength'],
        'timestamp': data['LastModified'].isoformat()
    }
    
    logger.info(object_info)
    return object_info