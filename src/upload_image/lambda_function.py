import os
import boto3
import json
import uuid
import base64

s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

def parse_key_value_string(key_value_string):
    """Parses a command-separated key:value string into a dictionary."""
    try:
        return dict(item.split(":") for item in key_value_string.split(","))
    except ValueError:
        raise ValueError("Invalid key:value format. Ensure the string is properly formatted.")


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

        if not file_extension:
            raise ValueError("Content-Type must specify a valid file extension (e.g., image/jpeg)")

        # Generate a unique image ID and S3 key
        image_id = str(uuid.uuid4())
        image_key = f"images/{image_id}.{file_extension}"

        # Upload the binary image data to S3
        s3_client.put_object(Bucket=bucket_name, Key=image_key, Body=image_data, ContentType=content_type)

        raw_metadata = event.get('queryStringParameters', {}).get('metadata', '')
        metadata_dict = parse_key_value_string(raw_metadata)
        metadata = {
            key: {'S': value} for key, value in metadata_dict.items()
        }
        metadata["image_id"] = {'S': image_id}
        metadata["content_type"] = {'S': content_type}

        # Parse tags (optional)
        raw_tags = event.get('queryStringParameters', {}).get('tags', None)
        if raw_tags:
            tags = raw_tags.split(",")  # Split tags by comma
            metadata["tags"] = {'L': [{'S': tag.strip()} for tag in tags]}  # Store as a list of strings


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

lambda_handler(None, None)