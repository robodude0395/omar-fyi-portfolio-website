# Implementation Plan: Post Gallery

## Overview

Incrementally build the post gallery feature by first extending the content schema, then creating the gallery components (item → grid → button → lightbox), wiring them into the blog layout, adding the CLI init script, and finally documenting the setup in the README.

## Tasks

- [x] 1. Extend content schema
  - [x] 1.1 Add optional `gallery` field to blog content schema in `frontend/src/content/config.ts`
    - Add `gallery: z.string().min(1).optional()` to the existing blog schema object
    - _Requirements: 1.1, 1.4_

- [x] 2. Create GalleryItem component
  - [x] 2.1 Create `frontend/src/components/GalleryItem.astro`
    - Accept props: `src`, `description`, `type` ("image" | "video"), `index`
    - Render `<img loading="lazy">` for images with `alt` derived from description or filename fallback
    - Render `<video>` for videos with poster/preview
    - Add hover overlay for description (semi-transparent background, large readable text)
    - Hide overlay when no description is provided
    - Style with site CSS custom properties
    - Add rounded corners and consistent spacing per site patterns
    - _Requirements: 4.4, 4.5, 4.6, 5.1–5.5, 7.3, 8.1_

- [x] 3. Create Gallery component with manifest loading and masonry layout
  - [x] 3.1 Create `frontend/src/components/Gallery.astro`
    - Accept `folder` prop (string)
    - In frontmatter block, read `public/media/{folder}/gallery.json` via Node.js `fs` if it exists
    - If manifest exists, resolve items in manifest order, filtering to only listed files
    - If no manifest, auto-discover supported files sorted alphabetically
    - Classify each file as "image" or "video" by extension
    - Render a `<section id="gallery">` with an `<h2>` heading
    - Use CSS `column-count` for masonry layout: 3 columns desktop (>1024px), 2 tablet (641–1024px), 1 mobile (≤640px)
    - Render each resolved item as a `<GalleryItem>` component
    - _Requirements: 2.1–2.7, 4.1–4.3, 4.6, 7.6, 8.1–8.3_

- [x] 4. Create GalleryButton component
  - [x] 4.1 Create `frontend/src/components/GalleryButton.astro`
    - Accept optional `targetId` prop (defaults to "gallery")
    - Render a full-width, prominent anchor link that smooth-scrolls to `#{targetId}`
    - Label with gallery-access text (e.g., "View Gallery" or "Behind the Scenes")
    - Style consistently with site design system
    - _Requirements: 3.1–3.4, 8.1_

- [x] 5. Create GalleryLightbox component
  - [x] 5.1 Create `frontend/src/components/GalleryLightbox.astro`
    - Render a hidden full-viewport overlay with dark semi-transparent backdrop
    - Include close button, prev/next navigation, media container, and description area
    - Add client-side `<script>` that:
      - Listens for `gallery:open` custom events from GalleryItem clicks
      - Displays clicked item's media (image scaled to fit viewport, video with controls)
      - Shows description below media when available
      - Handles close on button click, click outside media, or Escape key
      - Handles prev/next navigation via controls and left/right arrow keys
      - Traps keyboard focus within the overlay while open
    - Handle touch devices: first tap shows description, second tap opens lightbox
    - Style with site CSS custom properties for dark/light theme support
    - _Requirements: 6.1–6.8, 7.1, 7.2, 7.4, 7.5, 8.1, 8.2_

- [x] 6. Wire gallery into BlogPost layout
  - [x] 6.1 Modify `frontend/src/layouts/BlogPost.astro`
    - Import `GalleryButton`, `Gallery`, and `GalleryLightbox` components
    - Check `post.data.gallery` to determine if gallery is enabled
    - Render `GalleryButton` after post content and before post footer
    - Render `Gallery` and `GalleryLightbox` after the footer (gallery as appendix)
    - When `gallery` field is omitted/undefined, render no gallery markup
    - _Requirements: 1.2, 1.3, 3.1_

- [x] 7. Create gallery init CLI script
  - [x] 7.1 Create `frontend/scripts/gallery-init.ts`
    - Accept folder name as CLI argument
    - Resolve path to `frontend/public/media/{folder-name}`
    - Exit with error (code 1) if folder does not exist
    - Warn and exit (code 0) if `gallery.json` already exists
    - Scan for supported extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.mp4`, `.webm`
    - Warn and exit if no supported files found
    - Write `gallery.json` with entries sorted alphabetically, each with `file` and empty `description`
    - Print summary: "{n} items added → {path}"
    - _Requirements: 9.1–9.8_

  - [x] 7.2 Add `gallery:init` script entry to `frontend/package.json`
    - Add `"gallery:init": "npx tsx scripts/gallery-init.ts"` to the scripts section
    - _Requirements: 9.1_

- [x] 8. Add gallery setup documentation to README
  - [x] 8.1 Add a brief "Post Gallery" section to the root `README.md`
    - How to enable: add `gallery: "folder-name"` to post frontmatter
    - How to scaffold: `npm run gallery:init -- folder-name`
    - Brief `gallery.json` format description
    - Keep it short and practical

## Manual Testing Checklist

Use this while developing to verify things work as you go:

- [x] Post without `gallery` field renders normally with no gallery button or section
- [x] Post with `gallery: "folder-name"` shows the gallery button after post content
- [x] Clicking the gallery button smooth-scrolls to the gallery section
- [x] Gallery displays images in a masonry grid (3 cols desktop, 2 tablet, 1 mobile)
- [x] Videos render with a visible preview/poster frame
- [x] Hovering an item with a description shows the overlay text
- [x] Hovering an item without a description shows no overlay
- [ ] Clicking an item opens the lightbox with the media full-size
- [ ] Lightbox shows description below the media when available
- [ ] Lightbox prev/next buttons navigate between items
- [ ] Left/right arrow keys navigate in the lightbox
- [ ] Escape key closes the lightbox
- [ ] Clicking outside the media closes the lightbox
- [ ] Tab key cycles focus within the lightbox (close, prev, next)
- [ ] Gallery works on mobile (tap for description, tap again for lightbox)
- [ ] Gallery looks correct in both dark and light color schemes
- [ ] `npm run gallery:init -- folder-name` generates a valid `gallery.json`
- [ ] Init script warns if `gallery.json` already exists
- [ ] Init script errors if folder doesn't exist
- [ ] Gallery with `gallery.json` shows items in manifest order
- [ ] Gallery without `gallery.json` auto-discovers and sorts files alphabetically
