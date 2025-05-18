#!/bin/bash
set -e

echo "Deploying CloudFormation stack: $STACK_NAME"
# Generate a simple hash using current time
DEPLOYMENT_HASH=$(date +%s)
echo "Generated DeploymentHash: $DEPLOYMENT_HASH"
$AWS_CMD cloudformation deploy \
  --stack-name $STACK_NAME \
  --template-file deployment/cloudformation.yaml \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Environment=$ENV \
    DeployBucket=$DEPLOY_BUCKET_NAME \
    DeployKeyPrefix="$DEPLOY_KEY_PREFIX" \
    DeploymentHash="$DEPLOYMENT_HASH"

echo "Deployment complete."
