import os
import unittest
from unittest.mock import patch

from src.delete_image import lambda_function


class TestDeleteImageLambda(unittest.TestCase):

    def setUp(self):
        os.environ['BUCKET_NAME'] = "test-bucket"
        os.environ['TABLE_NAME'] = "test-table"

    @patch('src.delete_image.lambda_function.s3_client')
    @patch('src.delete_image.lambda_function.dynamodb_client')
    def test_successful_deletion(self, mock_dynamodb_client, mock_s3_client):
        mock_s3_client.delete_object.return_value = {}
        mock_dynamodb_client.delete_item.return_value = {
            'Attributes': {'imageKey': {'S': 'images/test-image-id.jpg'}}
        }

        event = {
            "pathParameters": {
                "id": "test-image-id"
            }
        }

        response = lambda_function.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Image deleted successfully', response['body'])
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="images/test-image-id.jpg"
        )
        mock_dynamodb_client.delete_item.assert_called_once_with(
            TableName="test-table", Key={'imageId': {'S': 'test-image-id'}}, ReturnValues="ALL_OLD"
        )

    @patch('src.delete_image.lambda_function.s3_client')
    @patch('src.delete_image.lambda_function.dynamodb_client')
    def test_s3_deletion_failure(self, mock_dynamodb_client, mock_s3_client):
        mock_s3_client.delete_object.side_effect = Exception("S3 deletion error")
        mock_dynamodb_client.delete_item.return_value = {
            'Attributes': {'imageKey': {'S': 'images/test-image-id.jpg'}}
        }

        event = {
            "pathParameters": {
                "id": "test-image-id"
            }
        }

        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('S3 deletion error', response['body'])
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="images/test-image-id.jpg"
        )
        mock_dynamodb_client.delete_item.assert_called_once_with(
            TableName="test-table", Key={'imageId': {'S': 'test-image-id'}}, ReturnValues="ALL_OLD"
        )

    @patch('src.delete_image.lambda_function.s3_client')
    @patch('src.delete_image.lambda_function.dynamodb_client')
    def test_dynamodb_deletion_failure(self, mock_dynamodb_client, mock_s3_client):
        mock_s3_client.delete_object.return_value = {}
        mock_dynamodb_client.delete_item.side_effect = Exception("DynamoDB deletion error")

        event = {
            "pathParameters": {
                "id": "test-image-id"
            }
        }

        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DynamoDB deletion error', response['body'])
        mock_s3_client.delete_object.assert_not_called()
        mock_dynamodb_client.delete_item.assert_called_once_with(
            TableName="test-table", Key={'imageId': {'S': 'test-image-id'}}, ReturnValues="ALL_OLD"
        )


if __name__ == '__main__':
    unittest.main()
