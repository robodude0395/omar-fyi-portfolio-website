output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (used for cache invalidation)"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.cloudfront.domain_name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket hosting site content"
  value       = module.s3.bucket_id
}

output "acm_certificate_arn" {
  description = "ARN of the ACM TLS certificate"
  value       = module.acm.certificate_arn
}

output "name_servers" {
  description = "Route53 hosted zone name servers — point your domain registrar here"
  value       = module.route53.name_servers
}
