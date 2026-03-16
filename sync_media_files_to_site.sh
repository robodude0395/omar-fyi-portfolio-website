#!/usr/bin/env bash
#
# Syncs the local frontend/public/media/ folder to the S3 bucket's media/ prefix.
#
# - Overwrites remote files when local files share the same name
# - Deletes remote files that no longer exist locally
# - Pulls the bucket name from Terraform output automatically
#
# Usage:
#   ./sync_media_files_to_site.sh                     # auto-detect bucket from terraform
#   ./sync_media_files_to_site.sh my-bucket-name      # pass bucket name explicitly
#
# Requires: aws cli v2, terraform (if auto-detecting bucket)

set -euo pipefail

LOCAL_MEDIA_DIR="$(cd "$(dirname "$0")" && pwd)/frontend/public/media"
S3_BUCKET="${1:-}"

# ── Resolve bucket name ──────────────────────────────────────────────────────
if [[ -z "$S3_BUCKET" ]]; then
  echo "No bucket name provided — reading from Terraform output..."
  S3_BUCKET=$(terraform -chdir="$(dirname "$0")/terraform" output -raw s3_bucket_name 2>/dev/null) || true

  if [[ -z "$S3_BUCKET" ]]; then
    echo "Error: Could not determine S3 bucket name."
    echo "Either pass it as an argument or ensure 'terraform output s3_bucket_name' works."
    exit 1
  fi
fi

# ── Validate local media directory ────────────────────────────────────────────
if [[ ! -d "$LOCAL_MEDIA_DIR" ]]; then
  echo "Error: Local media directory not found at $LOCAL_MEDIA_DIR"
  exit 1
fi

# ── Sync ──────────────────────────────────────────────────────────────────────
echo "Syncing media to s3://$S3_BUCKET/media/ ..."
echo "  Source: $LOCAL_MEDIA_DIR"

aws s3 sync "$LOCAL_MEDIA_DIR" "s3://$S3_BUCKET/media/" \
  --delete \
  --cache-control "public, max-age=31536000, immutable"

echo "Done! Media synced successfully."
