# 🚀 Quick Start Guide

This guide will help you deploy the Self-Service Slack Bot Blueprint in minutes.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

- **AWS CLI** - [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS SAM CLI** - [Install SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Terraform** - [Install Terraform](https://developer.hashicorp.com/terraform/install)
- **AWS Account** with appropriate permissions
- **AWS Credentials** configured (`aws configure`)
- **Slack App** created - [Create a Slack App](https://api.slack.com/apps)

## Step 1: Configure Your Bot Name and Region

**⚠️ IMPORTANT:** Before running `make all`, you must set your bot name and AWS region.

### 1.1 Set Your Bot Name

Open the `Makefile` and replace `REPLACE_WITH_YOUR_BOT_NAME` with your desired bot name:

```makefile
# Example: BOT_NAME = my-slack-bot
BOT_NAME = REPLACE_WITH_YOUR_BOT_NAME
```

Choose a descriptive name like `my-slack-bot`, `devops-bot`, etc.

### 1.2 Set Your AWS Region

In the same `Makefile`, replace `REPLACE_WITH_YOUR_REGION` with your AWS region:

```makefile
# Example: AWS_REGION = us-east-1
AWS_REGION = REPLACE_WITH_YOUR_REGION
```

Common regions: `us-east-1`, `us-west-2`, `eu-west-1`, `ap-southeast-1`

### Quick Edit Command

You can quickly set both values by running:

```bash
# Replace 'my-slack-bot' and 'us-east-1' with your values
sed -i '' 's/REPLACE_WITH_YOUR_BOT_NAME/my-slack-bot/g' Makefile
sed -i '' 's/REPLACE_WITH_YOUR_REGION/us-east-1/g' Makefile
```

**Note for Linux users:** Remove the `''` after `-i`:
```bash
sed -i 's/REPLACE_WITH_YOUR_BOT_NAME/my-slack-bot/g' Makefile
sed -i 's/REPLACE_WITH_YOUR_REGION/us-east-1/g' Makefile
```

## Step 2: Configure Terraform Backend (Important!)

Before deploying, you need to set up a Terraform backend to store your state file.

### Option A: Create a New S3 Bucket

```bash
# Replace 'your-unique-bucket-name' with your desired bucket name
# Use the same region you set in Step 1.2
aws s3 mb s3://your-unique-bucket-name --region us-east-1
```

### Option B: Use an Existing S3 Bucket

If you already have an S3 bucket, you can use that instead.

### Configure backend.tf

Create a `backend.tf` file in the `runners/` directory:

```bash
cat > runners/backend.tf << 'EOF'
terraform {
  backend "s3" {
    bucket = "your-unique-bucket-name"
    key    = "slack-bot/terraform.tfstate"
    region = "us-east-1"
  }
}
EOF
```

**Important:** Replace `your-unique-bucket-name` with your actual S3 bucket name and ensure the `region` matches what you set in Step 1.2.

## Step 3: Deploy All Resources

From the project root directory, run:

```bash
make all
```

This command will:
1. **Build** the SAM application (Lambda functions)
2. **Deploy** the CloudFormation stack with Lambda functions, API Gateway, and SQS
3. **Apply** Terraform configuration to create CodeBuild projects (Runners)

### What Happens During Deployment?

- **SAM Build**: Packages the Python Lambda functions
- **SAM Deploy**: Deploys the CloudFormation stack (first-time deployment uses `--guided` mode)
  - You'll be prompted to provide:
    - Stack name (default: `slack-bot-stack`)
    - AWS Region (default: `us-east-1`)
    - BotName parameter (e.g., `my-slack-bot`)
    - Confirmation for IAM role creation
    - Allow SAM CLI IAM role creation
- **Terraform Apply**: Creates CodeBuild projects for each action in `bot/src/slack_bot/actions/`

## Step 4: Configure Slack App

After deployment completes, you'll see outputs including the API Gateway URL.

### 4.1 Get the API Gateway URL

```bash
aws cloudformation describe-stacks \
  --stack-name slack-bot-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`SlackBotApiUrl`].OutputValue' \
  --output text
```

### 4.2 Configure Slack App Settings

1. Go to your [Slack App Management Console](https://api.slack.com/apps)
2. Select your app
3. Configure **Slash Commands**:
   - Command: `/menu` (or customize in bot code - see below)
   - URL: `<API_GATEWAY_URL>` (from Step 4.1)
   - Example: `https://abc123.execute-api.us-east-1.amazonaws.com/Prod/slack`
   - Short Description: `Open the bot menu`
4. Configure **Interactivity & Shortcuts**:
   - Request URL: `<API_GATEWAY_URL>` (same as above)
5. Save changes

**Note:** The default slash command is `/menu`. To use a different command (e.g., `/mybot`), update line 24 in `bot/src/slack_bot/main.py`:

```python
@app.command("/menu")  # Change "/menu" to your preferred command
```

After changing the command, rebuild and redeploy:

```bash
make build deploy
```

## Step 5: Configure Slack Credentials

Fill the Secrets Manager secret with your Slack app credentials.

### 5.1 Get Your Slack Credentials

From your Slack App settings:
- **Signing Secret**: Found under `Basic Information` → `App Credentials` → `Signing Secret`
- **Bot Token**: Found under `OAuth & Permissions` → `Bot User OAuth Token` (starts with `xoxb-`)

### 5.2 Update the Secret

```bash
# Replace <BotName> with the BotName parameter you provided during deployment
aws secretsmanager put-secret-value \
  --secret-id /<BotName>/slack-secret-token \
  --secret-string '{
    "slack_signing_secret": "YOUR_SIGNING_SECRET_HERE",
    "slack_bot_token": "YOUR_BOT_TOKEN_HERE"
  }'
```

**Example:**

```bash
aws secretsmanager put-secret-value \
  --secret-id /my-slack-bot/slack-secret-token \
  --secret-string '{
    "slack_signing_secret": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "slack_bot_token": "xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx"
  }'
```

## Step 6: Test Your Bot

1. Open Slack
2. Type the slash command: `/menu`
3. You should see a modal with a list of available actions
4. Select an action and fill out the modal form
5. Submit and watch the action execute via CodeBuild!

**Note:** If you customized the slash command in Step 4.2, use your custom command instead of `/menu`.

---

## 🛠️ Additional Commands

### Build Only

Build the SAM application without deploying:

```bash
make build
```

### Deploy Only

Deploy the SAM application (requires prior build):

```bash
make deploy
```

### Apply Terraform Only

Create/update CodeBuild projects:

```bash
make apply
```

### Clean Build Artifacts

Remove SAM build artifacts:

```bash
make clean
```

### Destroy Everything

Remove all resources (Terraform + CloudFormation):

```bash
make destroy
```

**Warning:** This will delete all resources including Lambda functions, API Gateway, CodeBuild projects, and associated data.

---

## 📝 Customization

### Change Stack Name

Edit the `Makefile`:

```makefile
STACK_NAME = my-custom-stack-name
```

### Change Bot Name or Region After Initial Setup

If you need to change your bot name or region after initial deployment:

1. Update the values in the `Makefile` (as described in Step 1)
2. Update `runners/backend.tf` if you changed regions
3. Run `make destroy` to remove old resources
4. Run `make all` to redeploy with new settings

---

## 🐛 Troubleshooting

### Issue: Terraform state file not found

**Solution:** Ensure you created the S3 bucket and updated `runners/backend.tf` with the correct bucket name.

### Issue: SAM deployment fails with "Unable to upload artifact"

**Solution:**
1. Check your AWS credentials have S3 permissions
2. SAM creates its own managed bucket for artifacts

### Issue: Slack says "dispatch_failed"

**Solution:**
1. Verify the API Gateway URL is correctly set in Slack App settings
2. Check that the Secrets Manager secret contains valid credentials
3. Review Lambda function logs in CloudWatch

### Issue: CodeBuild project not found

**Solution:** Run `make apply` to create/update CodeBuild projects after adding new actions.

### View Logs

Check Lambda function logs:

```bash
sam logs -n SlackBotFunction --stack-name slack-bot-stack --tail
```

Check CodeBuild logs:

```bash
aws codebuild batch-get-builds --ids <build-id>
```

---

## 🎯 Next Steps

- **Add Custom Actions**: See the main [README.md](./README.md) for instructions on creating new actions
- **Monitor Executions**: Use CloudWatch to monitor Lambda and CodeBuild executions
- **Customize Permissions**: Update IAM policies in `template.yaml` and `runners/main.tf` as needed

---

## 🆘 Need Help?

- Check the [README.md](./README.md) for architecture details
- Review AWS CloudFormation and Terraform documentation
- Visit [Senora.dev](https://Senora.dev) for platform services

Happy building! 🚀
