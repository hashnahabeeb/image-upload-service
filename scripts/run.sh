#!/bin/bash

case $1 in
  clean|build|upload|deploy|delete|describe|logs)
    ./scripts/$1.sh
    ;;
  *)
    echo "Usage: ./run.sh [clean|build|upload|deploy|delete|describe|logs]"
    ;;
esac
