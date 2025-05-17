#!/bin/bash
set -e

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

  echo "Waiting for stack update to complete..."
  awslocal cloudformation wait stack-update-complete --stack-name $STACK_NAME
else
  echo "Waiting for stack creation to complete..."
  awslocal cloudformation wait stack-create-complete --stack-name $STACK_NAME
fi

echo "Deployment complete."