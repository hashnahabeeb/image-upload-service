import os
import unittest
from unittest.mock import patch, MagicMock
import json
from src.view_image import lambda_function

class TestViewImageLambda(unittest.TestCase):

    def setUp(self):
        os.environ['BUCKET_NAME'] = "test-bucket"

    @patch('src.view_image.lambda_function.s3_client')
    def test_successful_url_generation(self, mock_s3_client):
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
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': "test-bucket", 'Key': "images/test-image-id.jpg"},
            ExpiresIn=3600
        )

    @patch('src.view_image.lambda_function.s3_client')
    def test_s3_client_error(self, mock_s3_client):
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
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': "test-bucket", 'Key': "images/test-image-id.jpg"},
            ExpiresIn=3600
        )

if __name__ == '__main__':
    unittest.main()