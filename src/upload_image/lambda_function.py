import os
import boto3
import json
import uuid
import base64

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    try:
        print("Received event: ", json.dumps(event, indent=2))

        is_base64_encoded = event.get('isBase64Encoded', False)
        image_data = event['body']
        if is_base64_encoded:
            image_data = base64.b64decode(image_data)

        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        file_extension = content_type.split('/')[-1]

        image_id = str(uuid.uuid4())
        image_key = f"images/{image_id}.{file_extension}"

        # Extract X-Image-Name header if present
        image_name = event['headers'].get('X-Image-Name') or event['headers'].get('x-image-name')

        # Upload the binary image data to S3
        s3_client.put_object(Bucket=bucket_name, Key=image_key, Body=image_data, ContentType=content_type)

        metadata = {
            "image_id": {'S': image_id},
            "content_type": {'S': content_type},
            "tags": {'L': []}
        }
        if image_name:
            metadata["image_name"] = {'S': image_name}

        query_params = event.get('queryStringParameters') or {}
        add_tags(metadata, query_params)
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'imageId': {'S': image_id},
                'imageKey': {'S': image_key},
                'metadata': {'M': metadata}
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


def add_tags(metadata, query_params):
    raw_tags = query_params.get('tags', None)
    if raw_tags:
        tags = raw_tags.split(",")
        metadata["tags"] = {
            'L': [
                {'M': {'key': {'S': tag.split(":")[0].strip()}, 'value': {'S': tag.split(":")[1].strip()}}}
                for tag in tags if ":" in tag
            ]
        }
