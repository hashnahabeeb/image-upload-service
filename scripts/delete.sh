#!/bin/bash
set -e

echo "Emptying S3 bucket: $BUCKET_NAME"
awslocal s3 rm s3://$BUCKET_NAME --recursive

echo "Deleting CloudFormation stack: $STACK_NAME"
awslocal cloudformation delete-stack --stack-name $STACK_NAME
