import boto3
import os

dynamo = boto3.client('dynamodb')
TABLE = 'DeadDropMetadata'

def lambda_handler(event, context):
    file_id = event['fileId']
    dynamo.update_item(
        TableName=TABLE,
        Key={'fileId': {'S': file_id}},
        UpdateExpression='SET available = :val',
        ExpressionAttributeValues={':val': {'BOOL': True}}
    )
    return {"status": "file marked available"}