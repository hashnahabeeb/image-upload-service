import os
import unittest
from unittest.mock import patch, MagicMock
import json
from src.upload_image import lambda_function

class TestUploadImageLambda(unittest.TestCase):

    def setUp(self):
        os.environ['BUCKET_NAME'] = "test-bucket"
        os.environ['TABLE_NAME'] = "test-table"

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_successful_upload(self, mock_dynamodb_client, mock_s3_client):
        # Mock S3 and DynamoDB responses
        mock_s3_client.put_object.return_value = {}
        mock_dynamodb_client.put_item.return_value = {}

        # Mock event
        event = {
            "body": json.dumps({
                "image_data": "dGVzdC1pbWFnZS1kYXRh",  # Base64 encoded string
                "metadata": {"user_id": "user123", "tags": ["tag1", "tag2"]}
            })
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 201)
        self.assertIn('Image uploaded successfully', response['body'])
        mock_s3_client.put_object.assert_called_once()
        mock_dynamodb_client.put_item.assert_called_once()

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_missing_required_fields(self, mock_dynamodb_client, mock_s3_client):
        # Mock event with missing fields
        event = {
            "body": json.dumps({
                "metadata": {"user_id": "user123", "tags": ["tag1", "tag2"]}
            })
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('error', response['body'])
        mock_s3_client.put_object.assert_not_called()
        mock_dynamodb_client.put_item.assert_not_called()

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_s3_upload_failure(self, mock_dynamodb_client, mock_s3_client):
        # Mock S3 failure
        mock_s3_client.put_object.side_effect = Exception("S3 upload error")

        # Mock event
        event = {
            "body": json.dumps({
                "image_data": "dGVzdC1pbWFnZS1kYXRh",  # Base64 encoded string
                "metadata": {"user_id": "user123", "tags": ["tag1", "tag2"]}
            })
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('S3 upload error', response['body'])
        mock_s3_client.put_object.assert_called_once()
        mock_dynamodb_client.put_item.assert_not_called()

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_dynamodb_put_failure(self, mock_dynamodb_client, mock_s3_client):
        # Mock S3 success
        mock_s3_client.put_object.return_value = {}

        # Mock DynamoDB failure
        mock_dynamodb_client.put_item.side_effect = Exception("DynamoDB put error")

        # Mock event
        event = {
            "body": json.dumps({
                "image_data": "dGVzdC1pbWFnZS1kYXRh",  # Base64 encoded string
                "metadata": {"user_id": "user123", "tags": ["tag1", "tag2"]}
            })
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DynamoDB put error', response['body'])
        mock_s3_client.put_object.assert_called_once()
        mock_dynamodb_client.put_item.assert_called_once()

if __name__ == '__main__':
    unittest.main()