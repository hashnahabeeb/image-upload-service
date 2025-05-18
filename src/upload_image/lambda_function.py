import base64
import json
import os
import uuid

import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')


def get_header(event, key):
    """
    Helper function to retrieve a header value.
    """
    return event['headers'].get(key) or event['headers'].get(key.lower())


def parse_tags(query_params):
    """
    Parse tags from query parameters into a DynamoDB-compatible format.
    """
    raw_tags = query_params.get('tags', None)
    if raw_tags:
        return {
            tag.split(":")[0].strip(): {'S': tag.split(":")[1].strip()}
            for tag in raw_tags.split(",") if ":" in tag
        }
    return {}


def lambda_handler(event, context):
    """
    Lambda function to handle image upload, store metadata in DynamoDB, and save the image in S3.
    """
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']

    try:
        print("Received event: ", json.dumps(event, indent=2))

        # Decode image data if base64 encoded
        is_base64_encoded = event.get('isBase64Encoded', False)
        image_data = base64.b64decode(event['body']) if is_base64_encoded else event['body']

        image_name = get_header(event, 'X-Image-Name')

        content_type = get_header(event, 'Content-Type')
        file_extension = content_type.split('/')[-1]

        # Generate a unique image ID and S3 key
        image_id = str(uuid.uuid4())
        image_key = f"images/{image_id}.{file_extension}"

        s3_client.put_object(Bucket=bucket_name, Key=image_key, Body=image_data, ContentType=content_type)

        # Prepare metadata for DynamoDB
        metadata = {
            "image_id": {'S': image_id},
            "content_type": {'S': content_type}
        }

        # Add image name to metadata if provided
        if image_name:
            metadata["image_name"] = {'S': image_name}

        # Add tags from query parameters
        query_params = event.get('queryStringParameters') or {}
        tags = parse_tags(query_params)

        # Store metadata in DynamoDB
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'imageId': {'S': image_id},
                'imageKey': {'S': image_key},
                'metadata': {'M': metadata},
                'tags': {'M': tags}
            }
        )

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Image uploaded successfully', 'imageId': image_id})
        }

    except Exception as e:
        # Handle errors and return failure response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
