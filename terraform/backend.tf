# ── Remote Backend Configuration ──────────────────────────────────────────────
#
# Uncomment the backend block below AFTER creating the S3 bucket for
# Terraform state. First-time setup:
#
#   1. Create an S3 bucket for state:
#      aws s3api create-bucket \
#        --bucket omar-fyi-terraform-state \
#        --region eu-west-2 \
#        --create-bucket-configuration LocationConstraint=eu-west-2
#
#   2. Enable versioning:
#      aws s3api put-bucket-versioning \
#        --bucket omar-fyi-terraform-state \
#        --versioning-configuration Status=Enabled
#
#   3. Enable encryption:
#      aws s3api put-bucket-encryption \
#        --bucket omar-fyi-terraform-state \
#        --server-side-encryption-configuration \
#          '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
#
#   4. Uncomment the block below and run: terraform init -migrate-state
#
# terraform {
#   backend "s3" {
#     bucket       = "omar-fyi-com-terraform-state"
#     key          = "portfolio/terraform.tfstate"
#     region       = "eu-west-2"
#     encrypt      = true
#     use_lockfile = true
#   }
# }
