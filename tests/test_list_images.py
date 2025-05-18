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
                    'imageKey': {'S': 'images/image1.jpg'},
                    'metadata': {'M': {'image_id': {'S': 'image1.jpg'}}},
                    'tags': {'M': {'tag1': {'S': 'value1'}}}
                },
                {
                    'imageId': {'S': 'image2'},
                    'imageKey': {'S': 'images/image2.jpg'},
                    'metadata': {'M': {'image_id': {'S': 'image2.jpg'}}},
                    'tags': {'M': {'tag1': {'S': 'value1'}}}
                }
            ]
        }

        # Mock event
        event = {
            "queryStringParameters": {
                "tags": "tag1:value1"
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
    def test_no_matching_images(self, mock_dynamodb_client):
        # Mock DynamoDB response
        mock_dynamodb_client.scan.return_value = {
            'Items': []
        }

        # Mock event with query parameters
        event = {
            "queryStringParameters": {
                "metadata": "image_id:nonexistent_img"
            }
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 0)

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
                "metadata": "image_id:123",
                "tags": "tag1:value1"
            }
        }

        # Call the Lambda function
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DynamoDB scan error', response['body'])


if __name__ == '__main__':
    unittest.main()
