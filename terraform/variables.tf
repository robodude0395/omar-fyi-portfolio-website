variable "domain_name" {
  description = "The domain name for the portfolio site (e.g. omar-fyi.com)"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. prod, staging)"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS region for most resources (S3, Route53, etc.)"
  type        = string
  default     = "eu-west-2"
}

variable "tags" {
  description = "Default tags applied to all resources"
  type        = map(string)
  default = {
    Project   = "portfolio"
    ManagedBy = "terraform"
  }
}
