#!/bin/bash
set -e

LAMBDA_DIRS=("upload_image" "list_images" "view_image" "delete_image")

for dir in "${LAMBDA_DIRS[@]}"; do
  echo "Zipping $dir..."
  (cd src/$dir && zip -qr ../../$ARTIFACTS_DIR/$dir.zip .)
done
# Copy the entire deployment folder to the artifacts directory
echo "Copying deployment folder to artifacts..."
cp -r deployment $ARTIFACTS_DIR/

echo "Deployment folder copied to artifacts."