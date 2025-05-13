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
    def test_successful_url_generation(self, mock_s3_client, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.get_item.return_value = {
            'Item': {'imageId': {'S': 'test-image-id'}}
        }

        # Mock S3 presigned URL generation
        mock_s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/images/test-image-id.jpg"

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
        body = json.loads(response['body'])
        self.assertIn('image_url', body)
        self.assertEqual(body['image_url'], "https://test-bucket.s3.amazonaws.com/images/test-image-id.jpg")
        mock_dynamodb_client.get_item.assert_called_once_with(
            TableName="test-table",
            Key={'imageId': {'S': 'test-image-id'}}
        )
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': "test-bucket", 'Key': "images/test-image-id.jpg"},
            ExpiresIn=3600
        )

    @patch('src.view_image.lambda_function.dynamodb_client')
    def test_image_not_found_in_dynamodb(self, mock_dynamodb_client):
        # Mock DynamoDB response for missing item
        mock_dynamodb_client.get_item.return_value = {}

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
        mock_dynamodb_client.get_item.assert_called_once_with(
            TableName="test-table",
            Key={'imageId': {'S': 'non-existent-image-id'}}
        )

    @patch('src.view_image.lambda_function.dynamodb_client')
    @patch('src.view_image.lambda_function.s3_client')
    def test_s3_client_error(self, mock_s3_client, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.get_item.return_value = {
            'Item': {'imageId': {'S': 'test-image-id'}}
        }

        # Mock S3 error
        mock_s3_client.generate_presigned_url.side_effect = Exception("S3 error")

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
        mock_dynamodb_client.get_item.assert_called_once_with(
            TableName="test-table",
            Key={'imageId': {'S': 'test-image-id'}}
        )
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': "test-bucket", 'Key': "images/test-image-id.jpg"},
            ExpiresIn=3600
        )

if __name__ == '__main__':
    unittest.main()