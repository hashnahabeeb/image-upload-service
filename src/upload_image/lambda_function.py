import os
import boto3
import json
import uuid

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    try:
        # Log the received event
        print("Received event: ", json.dumps(event, indent=2))

        # Decode the binary data from the body
        image_data = event['body']
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        file_extension = content_type.split('/')[-1]

        if not file_extension:
            raise ValueError("Content-Type must specify a valid file extension (e.g., image/jpeg)")

        # Generate a unique image ID and S3 key
        image_id = str(uuid.uuid4())
        image_key = f"images/{image_id}.{file_extension}"

        # Upload the binary image data to S3
        s3_client.put_object(Bucket=bucket_name, Key=image_key, Body=image_data, ContentType=content_type)

        # Save metadata to DynamoDB
        metadata = {
            "image_id": image_id,
            "content_type": content_type
        }
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