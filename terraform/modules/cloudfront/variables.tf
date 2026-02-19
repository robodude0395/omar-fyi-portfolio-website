variable "domain_name" {
  description = "Primary domain name"
  type        = string
}

variable "s3_bucket_id" {
  description = "S3 bucket name"
  type        = string
}

variable "s3_bucket_arn" {
  description = "S3 bucket ARN"
  type        = string
}

variable "s3_bucket_regional_domain_name" {
  description = "S3 bucket regional domain name"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate (must be in us-east-1)"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}
