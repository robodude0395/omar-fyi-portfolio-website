output "distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.site.id
}

output "distribution_arn" {
  description = "CloudFront distribution ARN"
  value       = aws_cloudfront_distribution.site.arn
}

output "domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.site.domain_name
}

output "hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID (for Route53 alias)"
  value       = aws_cloudfront_distribution.site.hosted_zone_id
}
