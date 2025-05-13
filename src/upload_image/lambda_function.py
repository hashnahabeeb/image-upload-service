import os
import boto3
import base64
import json
import uuid

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    try:
        print("Received event: ", json.dumps(event, indent=2))
        body = json.loads(event['body'])
        image_data = body['image_data']
        metadata = body['metadata']

        image_id = str(uuid.uuid4())
        image_key = f"images/{image_id}.jpg"

        # Decode and upload the image to S3
        image_bytes = base64.b64decode(image_data)
        s3_client.put_object(Bucket=bucket_name, Key=image_key, Body=image_bytes)

        # Save metadata to DynamoDB
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'imageId': {'S': image_id},
                'imageKey': {'S': image_key},
                'metadata': {'S': json.dumps(metadata)}
            }
        )

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Image uploaded successfully', 'imageId': image_id})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
