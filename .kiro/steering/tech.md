# Tech Stack

## Frontend

- **Framework**: Astro 4.x (static site generator)
- **Language**: TypeScript (strict mode)
- **Content**: Markdown with frontmatter
- **Styling**: CSS (no framework mentioned)
- **Image Processing**: Sharp
- **Sitemap**: @astrojs/sitemap integration

## Infrastructure

- **Hosting**: AWS S3 (private bucket) + CloudFront CDN
- **DNS**: AWS Route 53
- **TLS**: AWS ACM (free, auto-renewing certificates)
- **IaC**: Terraform >= 1.5
- **Domain Registrar**: Cloudflare Registrar

## CI/CD

- **Platform**: GitHub Actions
- **Triggers**: Push to main (path-filtered) + manual dispatch
- **Build**: Node.js 20, npm ci
- **Deploy**: AWS CLI sync to S3 + CloudFront invalidation

## Development Requirements

- Node.js >= 20
- Terraform >= 1.5
- AWS CLI v2 (configured with credentials)

## Common Commands

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (http://localhost:4321)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Infrastructure Management

```bash
cd terraform

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Apply infrastructure changes
terraform apply

# View outputs (nameservers, bucket name, distribution ID)
terraform output
```

### Manual Deployment

```bash
# Build site
cd frontend && npm run build

# Sync to S3 (replace YOUR_BUCKET)
aws s3 sync dist/ s3://YOUR_BUCKET --delete

# Invalidate CloudFront cache (replace YOUR_DIST_ID)
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

## Build Configuration

- **Site URL**: https://omar-fyi.com (configured in astro.config.mjs)
- **Syntax Theme**: github-dark
- **TypeScript**: Extends astro/tsconfigs/strict
- **Cache Strategy**:
  - Static assets: `public, max-age=31536000, immutable`
  - HTML/dynamic: `public, max-age=0, must-revalidate`
  - Media folder excluded from sync (manually managed)
