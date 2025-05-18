import json
import os

import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    """
    Lambda function to delete an image and its metadata.
    Deletes the image metadata from DynamoDB and the corresponding image file from S3.
    """
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    try:
        print("Received event: ", json.dumps(event, indent=2))
        image_id = event['pathParameters']['id']

        # Delete metadata from DynamoDB and retrieve the old item
        response = dynamodb_client.delete_item(
            TableName=table_name,
            Key={'imageId': {'S': image_id}},
            ReturnValues="ALL_OLD"
        )
        image_key = response.get('Attributes', {}).get('imageKey', {}).get('S')
        if not image_key:
            raise ValueError("Image key not found in DynamoDB")

        # Delete image from S3
        s3_client.delete_object(Bucket=bucket_name, Key=image_key)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
