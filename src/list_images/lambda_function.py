import json
import os

import boto3
from boto3.dynamodb.types import TypeDeserializer

aws_region = boto3.session.Session().region_name
dynamodb_client = boto3.client('dynamodb')
deserializer = TypeDeserializer()


def deserialize_item(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def lambda_handler(event, context):
    """
    Lambda function to list images based on metadata and tags query parameters.
    """
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    print("Received event: ", json.dumps(event, indent=2))

    # Extract query parameters
    query_params = event.get('queryStringParameters') or {}
    metadata = query_params.get('metadata', None)
    tags = query_params.get('tags', None)

    # Initialize filter expression, attribute values, and attribute names
    filter_expressions = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    # Parse metadata query parameter
    if metadata:
        key, value = metadata.split(":")
        filter_expressions.append(f"metadata.#metadata_key = :metadata_value")
        expression_attribute_values[":metadata_value"] = {"S": value}
        expression_attribute_names["#metadata_key"] = key

    # Parse tags query parameter
    if tags:
        key, value = tags.split(":")
        filter_expressions.append(f"tags.#tags_key = :tags_value")
        expression_attribute_values[":tags_value"] = {"S": value}
        expression_attribute_names["#tags_key"] = key

    # Combine filter expressions
    filter_expression = " AND ".join(filter_expressions) if filter_expressions else None

    try:
        scan_params = {
            "TableName": table_name,
            **({"ExpressionAttributeValues": expression_attribute_values} if expression_attribute_values else {}),
            **({"FilterExpression": filter_expression} if filter_expression else {}),
            **({"ExpressionAttributeNames": expression_attribute_names} if expression_attribute_names else {}),
        }

        # Query DynamoDB
        response = dynamodb_client.scan(**scan_params)

        # Build response
        images = [
            {
                'selfLink': f'/images/{item["imageId"]}',
                'image_url': f'https://{bucket_name}.s3.{aws_region}.amazonaws.com/{item["imageKey"]}',
                'metadata': item.get("metadata", {}),
                'tags': item.get("tags", {})
            }
            for item in map(deserialize_item, response['Items'])
        ]

        return {
            'statusCode': 200,
            'body': json.dumps(images)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
