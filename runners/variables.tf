variable "bot_name" {
  type    = string
  default = "senora"
}

variable "actions_path" {
  description = "Path to the directory containing actions' files."
  type        = string
  default     = "../bot/src/slack_bot/actions" 
}