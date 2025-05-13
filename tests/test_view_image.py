import base64
import os
import unittest
from unittest.mock import patch, MagicMock
import json
from src.view_image import lambda_function

class TestViewImageLambda(unittest.TestCase):

    def setUp(self):
        os.environ['BUCKET_NAME'] = "test-bucket"
        os.environ['TABLE_NAME'] = "test-table"

    @patch('src.view_image.lambda_function.dynamodb_client')
    @patch('src.view_image.lambda_function.s3_client')
    def test_successful_image_retrieval(self, mock_s3_client, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.query.return_value = {
            'Count': 1,
            'Items': [{'imageId': {'S': 'test-image-id'}}]
        }

        # Mock S3 response
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b'test-image-data')),
            'ContentType': 'image/jpeg'
        }

        # Mock event
        event = {
            "pathParameters": {
                "id": "test-image-id"
            }
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers']['Content-Type'], 'image/jpeg')
        self.assertEqual(response['headers']['Content-Disposition'], 'attachment; filename="test-image-id.jpg"')
        self.assertTrue(response['isBase64Encoded'])
        self.assertEqual(response['body'], base64.b64encode(b'test-image-data').decode('utf-8'))

        mock_dynamodb_client.query.assert_called_once_with(
            TableName="test-table",
            KeyConditionExpression="imageId = :image_id",
            ExpressionAttributeValues={":image_id": {"S": "test-image-id"}}
        )
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test-image-id.jpg"
        )

    @patch('src.view_image.lambda_function.dynamodb_client')
    def test_image_not_found_in_dynamodb(self, mock_dynamodb_client):
        # Mock DynamoDB response for missing item
        mock_dynamodb_client.query.return_value = {'Count': 0}

        event = {
            "pathParameters": {
                "id": "non-existent-image-id"
            }
        }

        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertEqual(body['error'], 'Image not found')
        mock_dynamodb_client.query.assert_called_once_with(
            TableName="test-table",
            KeyConditionExpression="imageId = :image_id",
            ExpressionAttributeValues={":image_id": {"S": "non-existent-image-id"}}
        )

    @patch('src.view_image.lambda_function.dynamodb_client')
    @patch('src.view_image.lambda_function.s3_client')
    def test_s3_client_error(self, mock_s3_client, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.query.return_value = {
            'Count': 1,
            'Items': [{'imageId': {'S': 'test-image-id'}}]
        }

        # Mock S3 error
        mock_s3_client.get_object.side_effect = Exception("S3 error")

        # Mock event
        event = {
            "pathParameters": {
                "id": "test-image-id"
            }
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('S3 error', body['error'])
        mock_dynamodb_client.query.assert_called_once_with(
            TableName="test-table",
            KeyConditionExpression="imageId = :image_id",
            ExpressionAttributeValues={":image_id": {"S": "test-image-id"}}
        )
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test-image-id.jpg"
        )

if __name__ == '__main__':
    unittest.main()