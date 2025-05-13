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
        response = dynamodb_client.get_item(
            TableName=table_name,
            Key={'imageId': {'S': image_id}}
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': f"images/{image_id}.jpg"},
            ExpiresIn=3600
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'image_url': url})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
