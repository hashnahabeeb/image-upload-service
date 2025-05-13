# Image Management API

This project provides a serverless API for managing image uploads, retrieval, and deletion using AWS services such as S3 and DynamoDB.

## Features

- **Upload Image**: Upload an image to S3 and store its metadata in DynamoDB.
- **List Images**: Retrieve a list of images based on query parameters.
- **View Image**: Generate a presigned URL to view an image.
- **Delete Image**: Delete an image from S3 and its metadata from DynamoDB.

## Technologies Used

- **Language**: Python
- **Framework**: AWS Lambda
- **Services**: AWS S3, AWS DynamoDB, AWS Lambda, AWS API Gateway
- **API Documentation**: OpenAPI 3.0 (Swagger)

## Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- `pip` for managing Python dependencies

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   
2. Testing
Unit tests are provided for all Lambda functions.

To run the tests:
    ```bash
        python -m unittest discover tests
    ```