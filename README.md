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
- **Services**: AWS S3, AWS DynamoDB
- **API Documentation**: OpenAPI 3.0 (Swagger)

## Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate permissions
- `pip` for managing Python dependencies

## Setup
