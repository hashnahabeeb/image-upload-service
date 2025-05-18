#!/bin/bash

export AWS_CMD=${AWS_CMD:-aws --endpoint-url=http://localhost:4566}
#export AWS_CMD=${AWS_CMD:-aws}
export REGION=${AWS_DEFAULT_REGION:-us-east-1}
export PORT=${PORT:-4566}

export ARTIFACTS_DIR=artifacts
export STACK_NAME=image-service-hh001
export ENV=dev
export DEPLOY_BUCKET_NAME=lambda-artifacts
export DEPLOY_KEY_PREFIX=hh001
export BUCKET_NAME=${STACK_NAME}-storage-bucket-${ENV}
export TEMPLATE_FILE=https://$DEPLOY_BUCKET_NAME.s3.$REGION.amazonaws.com/$DEPLOY_KEY_PREFIX/deployment/cloudformation.yaml

for arg in "$@"; do
  case $arg in
    clean|build|upload|deploy|delete|describe|tests|get_url)
      ./scripts/$arg.sh
      ;;
    *)
      echo "Invalid argument: $arg"
      echo "Usage: ./run.sh [clean|build|upload|deploy|delete|describe|tests|get_url]"
      exit 1
      ;;
  esac
done
