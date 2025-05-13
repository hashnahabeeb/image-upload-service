#!/bin/bash
set -e

ARTIFACTS_DIR=artifacts
LAMBDA_DIRS=("upload_image" "list_images" "view_image" "delete_image")

for dir in "${LAMBDA_DIRS[@]}"; do
  echo "Zipping $dir..."
  (cd src/$dir && zip -qr ../../$ARTIFACTS_DIR/$dir.zip .)
done
