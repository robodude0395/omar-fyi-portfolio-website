# Components

## PostCard.astro

Shared post card used on both the homepage (`pages/index.astro`) and blog listing (`pages/blog/index.astro`).

### What lives here

- Thumbnail image (size, aspect ratio, border radius, object-fit)
- Post metadata row (date, tags)
- Heading and description styling
- Responsive stacking at 480px breakpoint

### Props

| Prop           | Type       | Default | Notes                              |
| -------------- | ---------- | ------- | ---------------------------------- |
| `slug`         | `string`   | —       | Used to build the `/blog/…` link   |
| `title`        | `string`   | —       |                                    |
| `description`  | `string`   | —       |                                    |
| `pubDate`      | `Date`     | —       |                                    |
| `thumbnail`    | `string?`  | —       | Falls back to default placeholder  |
| `tags`         | `string[]` | `[]`    |                                    |
| `showTags`     | `boolean`  | `false` | Blog listing enables this          |
| `headingLevel` | `h2 / h3`  | `h2`    | `h3` on homepage, `h2` on blog     |

### Common tweaks

- Thumbnail size → change `width: 450px` in `.post-thumbnail`
- Thumbnail shape → change `aspect-ratio: 1.77` in `.post-thumbnail`
- Tag display limit → change `tags.slice(0, 3)` in the template

## Utility: `utils/posts.ts`

`getPublishedPosts()` returns all non-draft blog posts sorted newest-first. Both pages call this instead of duplicating the filter/sort logic.
