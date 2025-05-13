#!/bin/bash
set -e

LAMBDA_DIRS=("upload_image" "list_images" "view_image" "delete_image")

for dir in "${LAMBDA_DIRS[@]}"; do
  echo "Logs for $dir:"
  awslocal logs describe-log-groups | grep $dir || true
done
