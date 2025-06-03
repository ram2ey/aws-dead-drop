import boto3, uuid, base64
from datetime import datetime, timedelta
import json

s3 = boto3.client('s3')
dynamo = boto3.client('dynamodb')
step = boto3.client('stepfunctions')

BUCKET = 'dead-drop-files-yourname'
TABLE = 'DeadDropMetadata'
STATE_MACHINE_ARN = 'arn:aws:states:eu-north-1:233602497165:stateMachine:FileReleaseWorkflow'

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    file_data = base64.b64decode(body['file'])  # File in base64
    delay_minutes = int(body['delay'])          # e.g. 60
    expire_minutes = int(body['expire'])        # e.g. 1440

    file_id = str(uuid.uuid4())
    s3_key = f"{file_id}.bin"

    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=file_data)

    now = datetime.utcnow()
    release_time = now + timedelta(minutes=delay_minutes)
    expire_time = now + timedelta(minutes=expire_minutes)

    dynamo.put_item(
        TableName=TABLE,
        Item={
            'fileId': {'S': file_id},
            's3Key': {'S': s3_key},
            'releaseTime': {'S': release_time.isoformat()},
            'expireTime': {'S': expire_time.isoformat()},
            'available': {'BOOL': False}
        }
    )

    step.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=file_id,
        input=json.dumps({
            "fileId": file_id,
            "releaseTime": release_time.isoformat(),
            "expireTime": expire_time.isoformat()
        })
    )

    return {
        'statusCode': 200,
        'body': json.dumps({"fileId": file_id})
    }
