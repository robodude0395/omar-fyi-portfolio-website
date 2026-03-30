#!/usr/bin/env bash
#
# Syncs the local frontend/public/media/ folder to the S3 bucket's media/ prefix.
#
# Optimized for large media libraries (GBs / thousands of files):
#   - Parallel uploads via AWS CLI transfer config
#   - --size-only skips expensive MD5 checksums (media rarely changes in-place)
#   - Multipart threshold tuned for large files
#
# Usage:
#   ./sync_media_files_to_site.sh                     # auto-detect bucket from terraform
#   ./sync_media_files_to_site.sh my-bucket-name      # pass bucket name explicitly
#
# Requires: aws cli v2, terraform (if auto-detecting bucket)

set -euo pipefail

LOCAL_MEDIA_DIR="$(cd "$(dirname "$0")" && pwd)/frontend/public/media"
S3_BUCKET="${1:-}"

# ── Tuning knobs ─────────────────────────────────────────────────────────────
MAX_CONCURRENT=${MAX_CONCURRENT:-20}          # parallel upload threads
MULTIPART_THRESHOLD=${MULTIPART_THRESHOLD:-50MB}  # chunk files larger than this
MULTIPART_CHUNKSIZE=${MULTIPART_CHUNKSIZE:-25MB}  # size of each part

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

# ── Configure AWS CLI transfer settings for this run ─────────────────────────
export AWS_MAX_ATTEMPTS=5
aws configure set default.s3.max_concurrent_requests "$MAX_CONCURRENT"
aws configure set default.s3.multipart_threshold "$MULTIPART_THRESHOLD"
aws configure set default.s3.multipart_chunksize "$MULTIPART_CHUNKSIZE"

# ── Sync ──────────────────────────────────────────────────────────────────────
echo "Syncing media to s3://$S3_BUCKET/media/ ..."
echo "  Source:      $LOCAL_MEDIA_DIR"
echo "  Concurrency: $MAX_CONCURRENT threads"
echo "  Multipart:   threshold=$MULTIPART_THRESHOLD, chunk=$MULTIPART_CHUNKSIZE"
echo ""

aws s3 sync "$LOCAL_MEDIA_DIR" "s3://$S3_BUCKET/media/" \
  --delete \
  --size-only \
  --cache-control "public, max-age=31536000, immutable"

echo ""
echo "Done! Media synced successfully."
