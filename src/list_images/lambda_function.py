import os
import boto3
import json

aws_region = boto3.session.Session().region_name
dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    print("Received event: ", json.dumps(event, indent=2))
    user_id = event['queryStringParameters'].get('user_id', None)
    tags = event['queryStringParameters'].get('tags', None)

    # Build filter expression
    filter_expression = "contains(metadata, :user_id)" if user_id else ""
    if tags:
        filter_expression += " AND contains(metadata, :tags)" if filter_expression else "contains(metadata, :tags)"

    # DynamoDB query for images
    expression_attribute_values = {}
    if user_id:
        expression_attribute_values[":user_id"] = {"S": user_id}
    if tags:
        expression_attribute_values[":tags"] = {"S": tags}

    try:
        response = dynamodb_client.scan(
            TableName=table_name,
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        images = [
            {
                'image_url': f'https://{bucket_name}.s3.{aws_region}.amazonaws.com/images/{item["imageId"]["S"]}.jpg',
                'metadata': json.loads(item["metadata"]["S"])
            }
            for item in response['Items']
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
