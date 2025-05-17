import base64
import os
import boto3
import json

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

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
        image_key = response['Items'][0]['imageKey']['S']

        image_metadata = response['Items'][0]['metadata']['M']
        image_name = image_metadata['image_name']['S']
        content_type = image_metadata['content_type']['S']

        # Retrieve the image from S3
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=image_key)
        image_data = s3_response['Body'].read()

        # Return the image as a Base64-encoded response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename="{image_name}"'
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
