#!/bin/bash
set -e

DEPLOY_BUCKET_NAME=lambda-artifacts2
DEPLOY_KEY_PREFIX=hh001
ARTIFACTS_DIR=artifacts
LAMBDA_DIRS=("upload_image" "list_images" "view_image" "delete_image")

echo "Creating S3 bucket: $DEPLOY_BUCKET_NAME"
awslocal s3 mb s3://$DEPLOY_BUCKET_NAME || true

for dir in "${LAMBDA_DIRS[@]}"; do
  echo "Uploading $dir.zip to S3..."
  awslocal s3 cp $ARTIFACTS_DIR/$dir.zip s3://$DEPLOY_BUCKET_NAME/$DEPLOY_KEY_PREFIX/ || true
done

echo "S3 bucket contents:"
awslocal s3 ls s3://$DEPLOY_BUCKET_NAME --recursive
