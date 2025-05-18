#!/bin/bash
set -e

echo "Creating S3 bucket: $DEPLOY_BUCKET_NAME"
$AWS_CMD s3 mb s3://$DEPLOY_BUCKET_NAME || true

echo "Uploading all contents of artifacts directory to S3 under prefix: $DEPLOY_KEY_PREFIX/"
$AWS_CMD s3 cp $ARTIFACTS_DIR/ s3://$DEPLOY_BUCKET_NAME/$DEPLOY_KEY_PREFIX/ --recursive || true

echo "S3 bucket contents:"
$AWS_CMD s3 ls s3://$DEPLOY_BUCKET_NAME/$DEPLOY_KEY_PREFIX/ --recursive
