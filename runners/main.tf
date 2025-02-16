locals {
  # List only directories from the actions_path
  directories = [for dir in fileset("${path.module}/${var.actions_path}", "*") : basename(dir) if can(file("${path.module}/${var.actions_path}/${dir}/buildspec.yaml"))]

  # Create the action data for each directory
  action_data = {
    for dir_name in local.directories : dir_name => {
      action_name        = dir_name
      action_source_file = "${var.actions_path}/${dir_name}/buildspec.yaml"
    }
  }
}

resource "aws_codebuild_project" "actions" {
  for_each = local.action_data

  name = "${var.bot_name}-${each.value.action_name}"

  source {
    type     = "S3"
    buildspec = file(each.value.action_source_file)
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:5.0"
    type         = "LINUX_CONTAINER"
  }

  artifacts {
    type = "NO_ARTIFACTS"
  }

  service_role = aws_iam_role.codebuild_role.arn
}

resource "aws_iam_role" "codebuild_role" {
  name = "${var.bot_name}-runners-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "codebuild_policy" {
  role   = aws_iam_role.codebuild_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "logs:*",
          "cloudwatch:*",
          "lambda:InvokeFunction"
        ]
        Resource = "*"
      }
    ]
  })
}
