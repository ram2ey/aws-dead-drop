import boto3

dynamo = boto3.client('dynamodb')
s3 = boto3.client('s3')

TABLE = 'DeadDropMetadata'
BUCKET = 'dead-drop-files-cloudsecdrop'  # Replace with your actual bucket name

def lambda_handler(event, context):
    file_id = event['fileId']
    
    # Get file key from DynamoDB
    response = dynamo.get_item(
        TableName=TABLE,
        Key={'fileId': {'S': file_id}}
    )
    
    s3_key = response['Item']['s3Key']['S']

    # Delete from S3
    s3.delete_object(Bucket=BUCKET, Key=s3_key)
    
    # Delete from DynamoDB
    dynamo.delete_item(
        TableName=TABLE,
        Key={'fileId': {'S': file_id}}
    )
    
    return {"status": "file and metadata deleted"}