#!/bin/bash
# Quick blog post scaffolder
# Usage: ./new-post.sh

BLOG_DIR="src/content/blog"

echo "📝 New Blog Post"
echo "================"

# Title
read -p "Title: " TITLE
if [ -z "$TITLE" ]; then
  echo "Title is required." && exit 1
fi

# Slug (filename)
DEFAULT_SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
read -p "Slug [$DEFAULT_SLUG]: " SLUG
SLUG=${SLUG:-$DEFAULT_SLUG}

# Format
read -p "Format (md/mdx) [md]: " FORMAT
FORMAT=${FORMAT:-md}
if [[ "$FORMAT" != "md" && "$FORMAT" != "mdx" ]]; then
  echo "Invalid format. Use 'md' or 'mdx'." && exit 1
fi

# Description
read -p "Description: " DESCRIPTION

# Gallery
read -p "Gallery folder (leave empty for none): " GALLERY

# Today's date
PUB_DATE=$(date +%Y-%m-%d)

# Build the file
FILE="$BLOG_DIR/$SLUG.$FORMAT"

if [ -f "$FILE" ]; then
  echo "⚠️  File already exists: $FILE"
  read -p "Overwrite? (y/n) [n]: " OVERWRITE
  if [[ "$OVERWRITE" != "y" && "$OVERWRITE" != "Y" ]]; then
    echo "Aborted." && exit 0
  fi
fi

GALLERY_LINE=""
if [ -n "$GALLERY" ]; then
  GALLERY_LINE="gallery: \"$GALLERY\""
fi

cat > "$FILE" << EOF
---
title: "$TITLE"
description: "$DESCRIPTION"
pubDate: $PUB_DATE
thumbnail: ""
heroImage: ""
$GALLERY_LINE
---
EOF

# Add mdx imports if mdx
if [ "$FORMAT" == "mdx" ]; then
  cat >> "$FILE" << 'EOF'
import MediaEmbed from '../../components/MediaEmbed.astro';
import LinkCard from '../../components/LinkCard.astro';
import DownloadCard from '../../components/DownloadCard.astro';

EOF
fi

# Add starter content
cat >> "$FILE" << 'EOF'

# Introduction

Write your post here...
EOF

echo ""
echo "✅ Created: $FILE"
echo "   Open it and start writing!"
