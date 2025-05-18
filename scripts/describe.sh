#!/bin/bash
set -e

#$AWS_CMD cloudformation describe-stacks --stack-name $STACK_NAME
$AWS_CMD cloudformation describe-stack-events --stack-name $STACK_NAME \
    --query "StackEvents[*].[ResourceType,ResourceStatus,ResourceStatusReason]" \
    --output table
