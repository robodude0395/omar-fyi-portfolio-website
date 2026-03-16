# Project Structure

## Root Layout

```
portfolio_site/
├── frontend/           # Astro static site
├── terraform/          # Infrastructure as Code
├── .github/workflows/  # CI/CD pipelines
├── images/             # Architecture diagrams
└── .kiro/              # Kiro AI assistant configuration
```

## Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── content/
│   │   ├── blog/           # Markdown blog posts
│   │   └── config.ts       # Content collection schemas (Zod validation)
│   ├── layouts/
│   │   ├── BaseLayout.astro   # Site-wide layout wrapper
│   │   └── BlogPost.astro     # Blog post template
│   ├── pages/
│   │   ├── blog/
│   │   │   ├── index.astro       # Blog listing page
│   │   │   └── [...slug].astro   # Dynamic post routes
│   │   ├── index.astro           # Homepage
│   │   ├── about.astro           # About page
│   │   ├── 404.astro             # Custom 404 page
│   │   └── robots.txt.ts         # Generated robots.txt
│   ├── assets/images/      # Build-time processed images
│   └── env.d.ts            # TypeScript environment definitions
├── public/
│   ├── media/              # Static media (excluded from deploy sync)
│   └── favicon.svg
├── astro.config.mjs        # Astro configuration
├── package.json
└── tsconfig.json
```

## Infrastructure Structure (`terraform/`)

```
terraform/
├── modules/
│   ├── s3/                 # S3 bucket + versioning + encryption
│   ├── cloudfront/         # CDN + OAC + URL rewrite function
│   ├── acm/                # TLS certificate (us-east-1)
│   └── route53/            # DNS hosted zone + records
├── main.tf                 # Root module + provider config
├── variables.tf            # Input variables
├── outputs.tf              # Output values (nameservers, IDs)
├── backend.tf              # Remote state configuration
├── terraform.tfvars        # Variable values (gitignored)
└── terraform.tfvars.example
```

## Content Organization

### Blog Posts

- Location: `frontend/src/content/blog/*.md`
- Schema: Defined in `frontend/src/content/config.ts`
- Required frontmatter: `title`, `description`, `pubDate`
- Optional frontmatter: `updatedDate`, `heroImage`, `thumbnail`, `tags`, `draft`
- Draft posts (`draft: true`) are hidden from listings

### Static Assets

- **Build-time images**: `frontend/src/assets/images/` (processed by Sharp)
- **Runtime media**: `frontend/public/media/` (served as-is, excluded from deploy sync)
- **Favicon**: `frontend/public/favicon.svg`

## Module Conventions

### Terraform Modules

Each module follows a consistent structure:
- `main.tf` - Resource definitions
- `variables.tf` - Input variables
- `outputs.tf` - Output values

### Astro Components

- `.astro` files for components and pages
- TypeScript for logic and type safety
- Markdown for content with frontmatter metadata

## Key Paths

- Dev server: `http://localhost:4321`
- Build output: `frontend/dist/`
- Terraform state: `terraform/terraform.tfstate` (local) or S3 (remote)
- GitHub Actions: `.github/workflows/deploy.yml` (frontend), `terraform.yml` (infrastructure)

## Naming Conventions

- Files: kebab-case (e.g., `blog-post.md`, `base-layout.astro`)
- Terraform resources: snake_case (e.g., `s3_bucket`, `cloudfront_distribution`)
- TypeScript: camelCase for variables, PascalCase for types
- S3 bucket naming: `{domain-with-dashes}-{environment}` (e.g., `omar-fyi-com-production`)
