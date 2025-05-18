import base64
import json
import os

import boto3
from boto3.dynamodb.types import TypeDeserializer

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

deserializer = TypeDeserializer()
deserialize = lambda item: {k: deserializer.deserialize(v) for k, v in item.items()}


def lambda_handler(event, context):
    """
    Lambda function to retrieve an image from S3 and return it as a Base64-encoded response.
    """
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']

    try:
        print("Received event:", json.dumps(event, indent=2))

        image_id = event['pathParameters']['id']

        # Query DynamoDB for image metadata
        response = dynamodb_client.query(
            TableName=table_name,
            KeyConditionExpression="imageId = :image_id",
            ExpressionAttributeValues={
                ":image_id": {"S": image_id}
            }
        )

        # Handle case where image is not found
        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }

        # Extract metadata and S3 key
        item = deserialize(response['Items'][0])
        image_key = item['imageKey']
        image_name = item['metadata']['image_name']
        content_type = item['metadata']['content_type']

        # Retrieve the image from S3
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=image_key)
        image_data = s3_response['Body'].read()

        is_download = (event.get('queryStringParameters') or {}).get('isDownload', 'false').lower() == 'true'
        # Return the image as a Base64-encoded response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                # If isDownload = true, add Content-Disposition header
                **({'Content-Disposition': f'attachment; filename="{image_name}"'} if is_download else {})
            },
            'body': base64.b64encode(image_data),
            'isBase64Encoded': True
        }

    except Exception as e:
        # Handle unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
