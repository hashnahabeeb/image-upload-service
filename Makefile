PROJECT_NAME=image-upload-service
ARTIFACTS_DIR=artifacts
BUCKET_NAME=lambda-artifacts
STACK_NAME=image-upload-stack
TEMPLATE_FILE=cloudformation/$(PROJECT_NAME).yaml
ENV=dev
ENDPOINT_URL=http://localhost:4566

LAMBDA_DIRS=upload_image list_images view_image delete_image

# Default target
all: clean build upload deploy

.PHONY: clean build upload deploy delete describe logs

clean:
	rm -rf $(ARTIFACTS_DIR)
	mkdir -p $(ARTIFACTS_DIR)

build:
	@for dir in $(LAMBDA_DIRS); do \
		echo "Zipping $$dir..."; \
		(cd lambda/$$dir && zip -qr ../../$(ARTIFACTS_DIR)/$$dir.zip .); \
	done

upload:
	@echo "Creating S3 bucket: $(BUCKET_NAME)"
	awslocal s3 mb s3://$(BUCKET_NAME) || true
	@for dir in $(LAMBDA_DIRS); do \
		echo "Uploading $$dir.zip to S3..."; \
		echo "awslocal s3 cp $(ARTIFACTS_DIR)/$$dir.zip s3://$(BUCKET_NAME)/"; \
		awslocal s3 cp $(ARTIFACTS_DIR)/$$dir.zip s3://$(BUCKET_NAME)/; \
	done

deploy:
	@echo "Deploying CloudFormation stack: $(STACK_NAME)"
	awslocal cloudformation create-stack \
		--stack-name $(STACK_NAME) \
		--template-body file://$(TEMPLATE_FILE) \
		--capabilities CAPABILITY_NAMED_IAM \
		--parameters ParameterKey=Environment,ParameterValue=$(ENV) || \
	awslocal cloudformation update-stack \
		--stack-name $(STACK_NAME) \
		--template-body file://$(TEMPLATE_FILE) \
		--capabilities CAPABILITY_NAMED_IAM \
		--parameters ParameterKey=Environment,ParameterValue=$(ENV)

delete:
	@echo "Deleting CloudFormation stack: $(STACK_NAME)"
	awslocal cloudformation delete-stack --stack-name $(STACK_NAME)

describe:
	awslocal cloudformation describe-stacks --stack-name $(STACK_NAME)

logs:
	@for dir in $(LAMBDA_DIRS); do \
		awslocal logs describe-log-groups | grep $$dir || true; \
	done
