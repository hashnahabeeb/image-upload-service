import base64
import os
import boto3
import json


s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    table_name = os.environ['TABLE_NAME']
    try:
        print("Received event: ", json.dumps(event, indent=2))
        image_id = event['pathParameters']['id']
        response = dynamodb_client.query(
            TableName=table_name,
            KeyConditionExpression="imageId = :image_id",
            ExpressionAttributeValues={
                ":image_id": {"S": image_id}
            }
        )

        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }

        s3_response = s3_client.get_object(
            Bucket=bucket_name,
            Key=f"images/{image_id}.jpg"
        )
        image_data = s3_response['Body'].read()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': "image/jpeg",
                'Content-Disposition': f'attachment; filename="{image_id}.jpg"'
            },
            'body': base64.b64encode(image_data).decode('utf-8'),
            'isBase64Encoded': True
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
