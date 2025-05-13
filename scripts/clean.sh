#!/bin/bash
set -e

ARTIFACTS_DIR=artifacts

echo "Cleaning artifacts..."
rm -rf $ARTIFACTS_DIR
mkdir -p $ARTIFACTS_DIR
