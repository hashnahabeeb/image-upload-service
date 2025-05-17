#!/bin/bash
set -e

awslocal cloudformation describe-stacks --stack-name $STACK_NAME
#awslocal cloudformation describe-stack-events --stack-name $STACK_NAME \
#    --query "StackEvents[*].[ResourceType,ResourceStatus,ResourceStatusReason]" \
#    --output table