#!/bin/bash
set -e

if [[ "$AWS_CMD" == "aws" ]]; then
  echo "Using AWS..."

  ApiEndpoint=$($AWS_CMD cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)

  if [ -z "$ApiEndpoint" ]; then
    echo "Error: ApiEndpoint not found in stack outputs."
    exit 1
  fi
else
  echo "Using LocalStack..."

  ApiId=$($AWS_CMD cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiId'].OutputValue" \
    --output text)

  if [ -z "$ApiId" ]; then
    echo "Error: ApiId not found in stack outputs."
    exit 1
  fi

  ApiEndpoint="http://localhost:${PORT}/restapis/${ApiId}/${ENV}/_user_request_"
fi

echo "ApiEndpoint: $ApiEndpoint"
