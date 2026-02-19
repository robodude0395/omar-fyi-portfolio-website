# Omar Maaouane — Portfolio & Blog

A minimal, fast, and cost-effective personal website built with Astro and hosted on AWS.

## Architecture

```
                    ┌─────────────┐
                    │  Route 53   │
                    │    (DNS)    │
                    └──────┬──────┘
                           │
                           ▼
┌──────────┐     ┌─────────────────┐     ┌─────────────┐
│  ACM     │────▶│   CloudFront    │────▶│     S3      │
│ (TLS)   │     │  (CDN + HTTPS)  │     │  (Storage)  │
└──────────┘     └─────────────────┘     └─────────────┘
                         ▲                       ▲
                         │                       │
                    ┌────┴────┐            ┌─────┴─────┐
                    │  Users  │            │  GitHub   │
                    │ (HTTPS) │            │  Actions  │
                    └─────────┘            │ (CI/CD)   │
                                           └───────────┘
```

**Flow:** Users hit the custom domain → Route 53 resolves to CloudFront → CloudFront serves cached content from S3 with TLS via ACM. GitHub Actions builds and deploys on every push to `main`.

## Tech Stack

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| Frontend       | [Astro](https://astro.build) 4.x       |
| Hosting        | AWS S3 + CloudFront                     |
| DNS            | AWS Route 53                            |
| TLS            | AWS ACM (free, auto-renewing)           |
| Infrastructure | Terraform                               |
| CI/CD          | GitHub Actions                          |

## Prerequisites

- [Node.js](https://nodejs.org) >= 20
- [Terraform](https://www.terraform.io/downloads) >= 1.5
- [AWS CLI](https://aws.amazon.com/cli/) v2, configured with credentials
- A registered domain name
- A GitHub account

## Project Structure

```
portfolio_site/
├── frontend/                    # Astro project
│   ├── src/
│   │   ├── content/
│   │   │   ├── blog/            # Markdown blog posts
│   │   │   └── config.ts        # Content collection schema
│   │   ├── layouts/
│   │   │   ├── BaseLayout.astro  # Site-wide layout
│   │   │   └── BlogPost.astro   # Blog post layout
│   │   └── pages/
│   │       ├── blog/
│   │       │   ├── index.astro  # Blog listing
│   │       │   └── [...slug].astro  # Dynamic post routes
│   │       ├── index.astro      # Homepage
│   │       ├── about.astro      # About page
│   │       ├── 404.astro        # Custom 404
│   │       └── robots.txt.ts    # Generated robots.txt
│   ├── public/
│   │   └── favicon.svg
│   ├── astro.config.mjs
│   ├── package.json
│   └── tsconfig.json
├── terraform/                   # Infrastructure as Code
│   ├── modules/
│   │   ├── s3/                  # S3 bucket + policy
│   │   ├── cloudfront/          # CDN distribution + OAC
│   │   ├── acm/                 # TLS certificate
│   │   └── route53/             # DNS records
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── backend.tf               # Remote state (commented)
│   └── terraform.tfvars.example
├── .github/workflows/
│   ├── deploy.yml               # Build + deploy to S3
│   └── terraform.yml            # Infrastructure CI/CD
├── .gitignore
└── README.md
```

## Local Development

### Frontend

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

### Writing Blog Posts

Create a new `.md` file in `frontend/src/content/blog/`:

```markdown
---
title: "Your Post Title"
description: "A brief description for listings and SEO."
pubDate: 2026-03-01
tags: ["topic", "another-topic"]
draft: false
---

Your content here. Full Markdown support with syntax highlighting.
```

Set `draft: true` to hide a post from listings while you work on it.

## Infrastructure Setup

### 1. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your domain name
```

### 2. Set Up Remote State (Optional but Recommended)

Follow the instructions in `backend.tf` to create an S3 bucket and DynamoDB table for state management. Then uncomment the backend configuration and run:

```bash
terraform init -migrate-state
```

### 3. Deploy Infrastructure

```bash
terraform init
terraform plan     # Review what will be created
terraform apply    # Create all resources
```

### 4. Update Domain Registrar

After `terraform apply`, note the name servers from the output:

```bash
terraform output name_servers
```

Update your domain registrar's nameservers to point to these Route 53 nameservers. DNS propagation may take up to 48 hours.

### 5. Configure GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

| Secret                        | Value                              |
|-------------------------------|------------------------------------|
| `AWS_ACCESS_KEY_ID`           | Your AWS access key                |
| `AWS_SECRET_ACCESS_KEY`       | Your AWS secret key                |
| `AWS_REGION`                  | `eu-west-2`                        |
| `S3_BUCKET`                   | From `terraform output s3_bucket_name` |
| `CLOUDFRONT_DISTRIBUTION_ID`  | From `terraform output cloudfront_distribution_id` |

### 6. Deploy the Site

Push to `main` or trigger the workflow manually:

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

The GitHub Action will build the Astro site, sync it to S3, and invalidate the CloudFront cache. Your site should be live within ~90 seconds.

## Deployment Workflow

### Automatic Deployment

- **Frontend changes** (`frontend/**`): Triggers the Build & Deploy workflow
- **Infrastructure changes** (`terraform/**`): Triggers the Terraform workflow

Both workflows also support manual triggers via `workflow_dispatch`.

### Manual Deployment

```bash
# Build
cd frontend && npm run build

# Deploy
aws s3 sync dist/ s3://YOUR_BUCKET --delete

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

## Cost Estimate

This setup is designed to be extremely cost-effective for a personal site:

| Service        | Cost                                              |
|----------------|---------------------------------------------------|
| **S3**         | ~$0.023/GB/month storage. A static site is a few MB — essentially free |
| **CloudFront** | 1 TB/month free for the first year, then ~$0.085/GB. A personal blog won't come close |
| **Route 53**   | $0.50/hosted zone/month + $0.40/million queries   |
| **ACM**        | Free (public certificates)                        |
| **Total**      | **~$1–2/month** after free tier                   |

For a personal portfolio with modest traffic, expect to pay roughly the cost of a coffee per month.

## Security

This setup follows AWS security best practices:

- **No public S3 access** — bucket is fully private, content served only through CloudFront via Origin Access Control (OAC)
- **HTTPS everywhere** — HTTP requests are automatically redirected to HTTPS
- **TLS 1.2+** — minimum protocol version enforced at CloudFront
- **Encryption at rest** — S3 bucket uses AES-256 server-side encryption
- **Versioning** — S3 versioning enabled for content protection
- **Least privilege** — CloudFront OAC grants read-only access to S3 objects
- **Infrastructure as Code** — all resources are defined, versioned, and auditable

## License

Content is © Omar Maaouane. Code is available for reference.
