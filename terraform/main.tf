terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ── Providers ──────────────────────────────────────────────────────────────────

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

# ACM certificates for CloudFront must be in us-east-1
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = var.tags
  }
}

# ── Modules ────────────────────────────────────────────────────────────────────

module "s3" {
  source = "./modules/s3"

  bucket_name                 = "${replace(var.domain_name, ".", "-")}-${var.environment}"
  environment                 = var.environment
  cloudfront_distribution_arn = module.cloudfront.distribution_arn
}

module "acm" {
  source = "./modules/acm"

  providers = {
    aws = aws.us_east_1
  }

  domain_name    = var.domain_name
  hosted_zone_id = module.route53.zone_id
}

module "cloudfront" {
  source = "./modules/cloudfront"

  domain_name                    = var.domain_name
  s3_bucket_id                   = module.s3.bucket_id
  s3_bucket_arn                  = module.s3.bucket_arn
  s3_bucket_regional_domain_name = module.s3.bucket_regional_domain_name
  acm_certificate_arn            = module.acm.certificate_arn
  environment                    = var.environment
}

module "route53" {
  source = "./modules/route53"

  domain_name               = var.domain_name
  cloudfront_domain_name    = module.cloudfront.domain_name
  cloudfront_hosted_zone_id = module.cloudfront.hosted_zone_id
}
