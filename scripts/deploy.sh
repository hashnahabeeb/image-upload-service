#!/bin/bash
set -e

STACK_NAME=image-upload-service
ENV=dev
TEMPLATE_FILE=deployment/cloudformation.yaml
DEPLOY_BUCKET_NAME=lambda-artifacts2
DEPLOY_KEY_PREFIX=hh001

echo "Deploying CloudFormation stack: $STACK_NAME"

if ! awslocal cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_FILE \
  --capabilities CAPABILITY_AUTO_EXPAND \
  --parameters \
    ParameterKey=Environment,ParameterValue=$ENV \
    ParameterKey=DeployBucket,ParameterValue=$DEPLOY_BUCKET_NAME \
    ParameterKey=DeployKeyPrefix,ParameterValue=$DEPLOY_KEY_PREFIX; then

  echo "Stack already exists. Updating..."
  awslocal cloudformation update-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --capabilities CAPABILITY_AUTO_EXPAND \
    --parameters \
      ParameterKey=Environment,ParameterValue=$ENV \
      ParameterKey=DeployBucket,ParameterValue=$DEPLOY_BUCKET_NAME \
      ParameterKey=DeployKeyPrefix,ParameterValue=$DEPLOY_KEY_PREFIX
fi
