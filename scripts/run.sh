#!/bin/bash

export ARTIFACTS_DIR=artifacts

export STACK_NAME=image-upload-service
export ENV=dev
export TEMPLATE_FILE=deployment/cloudformation.yaml
export DEPLOY_BUCKET_NAME=lambda-artifacts2
export DEPLOY_KEY_PREFIX=hh001
export BUCKET_NAME=image-upload-bucket-${ENV}

case $1 in
  clean|build|upload|deploy|delete|describe|logs)
    ./scripts/$1.sh
    ;;
  *)
    echo "Usage: ./run.sh [clean|build|upload|deploy|delete|describe|logs]"
    ;;
esac
