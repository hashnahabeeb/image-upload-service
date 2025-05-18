#!/bin/bash
set -e

echo "Emptying S3 bucket: $BUCKET_NAME"
$AWS_CMD s3 rm s3://$BUCKET_NAME --recursive || true

echo "Deleting CloudFormation stack: $STACK_NAME"
$AWS_CMD cloudformation delete-stack --stack-name $STACK_NAME

echo "Waiting for CloudFormation stack deletion to complete..."
$AWS_CMD cloudformation wait stack-delete-complete --stack-name $STACK_NAME

echo "CloudFormation stack deleted successfully."