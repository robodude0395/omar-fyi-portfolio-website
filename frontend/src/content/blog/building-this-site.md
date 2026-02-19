---
title: "Building This Site: Astro, AWS, and Terraform"
description: "A deep dive into the tech stack behind this site — static generation with Astro, hosting on S3 and CloudFront, infrastructure as code with Terraform, and CI/CD with GitHub Actions."
pubDate: 2026-02-18
tags: ["astro", "aws", "terraform", "infrastructure", "devops"]
draft: false
---

Every developer blog needs a post about how it was built. It's tradition. So here's mine.

## The requirements

I wanted something simple:

1. **Fast** — static HTML, no JavaScript framework overhead
2. **Cheap** — under £2/month
3. **Automated** — push to `main`, site updates
4. **Maintainable** — infrastructure as code, not click-ops
5. **Mine** — custom domain, full control

## The stack

### Astro for the frontend

[Astro](https://astro.build) is a static site generator that ships zero JavaScript by default. You write components, it outputs plain HTML and CSS. Perfect for a content site.

The killer feature is content collections. You define a schema for your blog posts, and Astro validates your frontmatter at build time. Type-safe markdown:

```typescript
const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});
```

No runtime, no hydration, no bundle size anxiety. Just HTML.

### S3 + CloudFront for hosting

The built site is a folder of static files. S3 stores them, CloudFront serves them globally with edge caching. The setup:

- **S3 bucket** — private, no public access. Files are only accessible through CloudFront using Origin Access Control (OAC)
- **CloudFront** — HTTPS everywhere, HTTP redirects, Brotli/gzip compression, custom error pages
- **Route53** — DNS management, A/AAAA records aliased to the CloudFront distribution
- **ACM** — free TLS certificate with automatic renewal

The total monthly cost:

| Service | Cost |
|---------|------|
| S3 storage | ~£0.01 (a few MB of HTML) |
| CloudFront | Free tier covers 1TB/month for the first year |
| Route53 | £0.40/hosted zone |
| ACM | Free |
| **Total** | **~£1-2/month** |

### Terraform for infrastructure

Every AWS resource is defined in Terraform. No clicking through the console. The infrastructure is split into modules:

```
terraform/
  modules/
    s3/          # Bucket, policy, encryption
    cloudfront/  # Distribution, OAC, caching
    acm/         # TLS certificate
    route53/     # DNS records
```

Want to tear it all down? `terraform destroy`. Want to see what would change? `terraform plan`. Want to recreate it identically in another account? `terraform apply`.

Infrastructure as code is one of those things that feels like overhead at first and then saves you the moment something goes wrong.

### GitHub Actions for CI/CD

Two workflows:

1. **Deploy** — triggered on push to `main` when frontend files change. Builds the Astro site, syncs to S3, invalidates the CloudFront cache.
2. **Terraform** — triggered on push to `main` when Terraform files change. Runs `fmt`, `validate`, `plan`, and `apply`.

The deploy step is three commands:

```bash
npm run build
aws s3 sync dist/ s3://$BUCKET --delete
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

Push, wait about 90 seconds, site is live.

## What I'd add next

- **RSS feed** — Astro makes this straightforward
- **Dark/light toggle** — currently follows system preference, might add a manual switch
- **Search** — probably Pagefind, which builds a search index at compile time
- **Analytics** — something privacy-respecting like Plausible or Umami

But for now, this works. Simple, fast, cheap, automated. Exactly what I wanted.
