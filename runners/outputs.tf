output "codebuild_project_names" {
  description = "List of CodeBuild project names created for actions."
  value       = [for project in aws_codebuild_project.actions : project.name]
}
