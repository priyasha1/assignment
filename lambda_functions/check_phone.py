import json
import boto3
from datetime import datetime
from boto3 import resource
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('dynamodb')
dynamodb_resource = resource('dynamodb')
tableName='customer_data'
table = dynamodb_resource.Table(tableName)


def lambda_handler(event, context):
    response = table.scan (
        Select='ALL_ATTRIBUTES',
        FilterExpression=Attr('telephone_number').eq(event['key1']))
    
    ret = 'Customer does not exists!'
    if response['Items']:
        for item in response['Items']:
            ret = 'Customer exists but does not have password!'
            if 'password' in item:
                ret = i.get('password') and 'Customer exists!'
    
    return {
        "message": ret
    }
                
            