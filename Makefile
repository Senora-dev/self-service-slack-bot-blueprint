# Makefile for SAM Build, SAM Deploy, Terraform Apply, and Destroy

# Set variables
AWS_REGION = us-east-1
STACK_NAME = slack-bot-stack

# Define default target
.PHONY: all
all: build deploy apply

# Build the SAM application
.PHONY: build
build:
	@echo "Building the Slack-Bot SAM application..."
	cd bot && sam build

# Deploy the SAM application with guided options
.PHONY: deploy
deploy:
	@echo "Deploying the SAM application..."
	cd bot && sam deploy --guided --region $(AWS_REGION) --stack-name $(STACK_NAME)

# Apply Terraform configuration
.PHONY: apply
apply:
	@echo "Creating CodeBuild projects (Runners) by applying Terraform configuration..."
	cd runners && terraform init && terraform apply -auto-approve

# Destroy Terraform resources and delete the SAM stack
.PHONY: destroy
destroy:
	@echo "Destroying Terraform resources..."
	cd runners && terraform destroy -auto-approve
	@echo "Deleting the SAM stack..."
	aws cloudformation delete-stack --stack-name $(STACK_NAME) --region $(AWS_REGION)
	@echo "Waiting for stack deletion to complete..."
	aws cloudformation wait stack-delete-complete --stack-name $(STACK_NAME) --region $(AWS_REGION)
	@echo "Cleanup completed."

# Clean up the build
.PHONY: clean
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf .aws-sam
