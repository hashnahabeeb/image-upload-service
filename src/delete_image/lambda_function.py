import os
import boto3
import json
from botocore.exceptions import ClientError

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')



def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    try:
        print("Received event: ", json.dumps(event, indent=2))
        image_id = event['pathParameters']['id']
        # Delete image from S3
        s3_client.delete_object(Bucket=bucket_name, Key=f"images/{image_id}.jpg")

        # Delete metadata from DynamoDB
        dynamodb_client.delete_item(
            TableName=table_name,
            Key={'imageId': {'S': image_id}}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }