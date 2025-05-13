import os
import unittest
from unittest.mock import patch, MagicMock
import json
from src.list_images import lambda_function

class TestListImagesLambda(unittest.TestCase):

    def setUp(self):
        os.environ['BUCKET_NAME'] = "test-bucket"
        os.environ['TABLE_NAME'] = "test-table"

    @patch('src.list_images.lambda_function.dynamodb_client')
    def test_successful_retrieval(self, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.scan.return_value = {
            'Items': [
                {
                    'imageId': {'S': 'image1'},
                    'metadata': {'S': json.dumps({'user_id': 'user123', 'tags': ['tag1', 'tag2']})}
                },
                {
                    'imageId': {'S': 'image2'},
                    'metadata': {'S': json.dumps({'user_id': 'user456', 'tags': ['tag3']})}
                }
            ]
        }

        # Mock event
        event = {
            "queryStringParameters": {
                "user_id": "user123",
                "tags": "tag1"
            }
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0]['image_url'], 'https://test-bucket.s3.us-east-1.amazonaws.com/images/image1.jpg')

    @patch('src.list_images.lambda_function.dynamodb_client')
    def test_missing_query_parameters(self, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.scan.return_value = {
            'Items': []
        }

        # Mock event with missing query parameters
        event = {
            "queryStringParameters": {}
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 0)

    @patch('src.list_images.lambda_function.dynamodb_client')
    def test_dynamodb_scan_failure(self, mock_dynamodb_client):
        # Mock DynamoDB failure
        mock_dynamodb_client.scan.side_effect = Exception("DynamoDB scan error")

        # Mock event
        event = {
            "queryStringParameters": {
                "user_id": "user123",
                "tags": "tag1"
            }
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DynamoDB scan error', response['body'])

if __name__ == '__main__':
    unittest.main()