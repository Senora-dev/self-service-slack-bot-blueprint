variable "bot_name" {
  type    = string
  default = "REPLACE_WITH_YOUR_BOT_NAME"
}

variable "actions_path" {
  description = "Path to the directory containing actions' files."
  type        = string
  default     = "../bot/src/slack_bot/actions" 
}