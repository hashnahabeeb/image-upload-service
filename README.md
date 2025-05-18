# Image Management API

This project provides a serverless API for managing image uploads, retrieval, and deletion using AWS services such as S3 and DynamoDB.

## Features

- **Upload Image**: Upload an image to S3 and store its metadata in DynamoDB.
- **List Images**: Retrieve a list of images based on query parameters.
- **View Image**: Download an image.
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
   ```
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Unit Testing
Unit tests are provided for all Lambda functions. To run the tests:
```
./run.sh clean
```

## API Documentation

The API is documented using OpenAPI 3.0 (Swagger). You can view the Swagger documentation by opening the following file:

[Swagger Documentation](deployment/swagger.yaml)

## Deployment
1. Clean the project:  
    ```
    ./run.sh clean
    ```
2. Build the project:
    ```
    ./run.sh build
    ```
3. Upload artifacts to S3:
    ```
    ./run.sh upload
    ``` 
4. Deploy the CloudFormation stack:
    ```
    ./run.sh deploy
    ```
5. Verify the deployment:
    ```
    ./run.sh describe
    ```
6. To get the url of the API:
    ```
    ./run.sh get_url
    ```
7. Delete the stack (if needed):
    ```
    ./run.sh delete
    ```