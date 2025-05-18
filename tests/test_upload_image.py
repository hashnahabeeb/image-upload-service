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
            "body": "MTIz",  # Base64 encoded image
            "headers": {
                "X-Image-Name": "test_image",
                "Content-Type": "image/png"
            },
            "isBase64Encoded": True,
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 201)
        body = json.loads(response['body'])
        self.assertIn('Image uploaded successfully', body['message'])
        self.assertIn('imageId', body)
        mock_s3_client.put_object.assert_called_once()
        mock_dynamodb_client.put_item.assert_called_once()

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_missing_required_fields(self, mock_dynamodb_client, mock_s3_client):
        # Mock event with missing fields
        event = {
            "headers": {
                "X-Image-Name": "test_image",
                "Content-Type": "image/png"
            },
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        mock_s3_client.put_object.assert_not_called()
        mock_dynamodb_client.put_item.assert_not_called()

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_invalid_base64_image_data(self, mock_dynamodb_client, mock_s3_client):
        # Mock event with invalid Base64 data
        event = {
            "body": "!!!notbase64@@@",  # Invalid Base64
            "headers": {
                "X-Image-Name": "test_image",
                "Content-Type": "image/png"
            },
            "isBase64Encoded": True,
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        self.assertIn('Invalid base64-encoded string', body['error'])
        mock_s3_client.put_object.assert_not_called()
        mock_dynamodb_client.put_item.assert_not_called()

    @patch('src.upload_image.lambda_function.s3_client')
    @patch('src.upload_image.lambda_function.dynamodb_client')
    def test_s3_upload_failure(self, mock_dynamodb_client, mock_s3_client):
        # Mock S3 failure
        mock_s3_client.put_object.side_effect = Exception("S3 upload error")

        # Mock event
        event = {
            "body": "MTIz",  # Base64 encoded image
            "headers": {
                "X-Image-Name": "test_image",
                "Content-Type": "image/png"
            },
            "isBase64Encoded": True,
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('S3 upload error', body['error'])
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
            "body": "MTIz",  # Base64 encoded image
            "headers": {
                "X-Image-Name": "test_image",
                "Content-Type": "image/png"
            },
            "isBase64Encoded": True,
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('DynamoDB put error', body['error'])
        mock_s3_client.put_object.assert_called_once()
        mock_dynamodb_client.put_item.assert_called_once()


if __name__ == '__main__':
    unittest.main()
