# Requirements Document

## Introduction

The Post Gallery feature adds an optional photo and video gallery appendix to blog posts. When a post has behind-the-scenes content (images and videos) stored in a media folder, the author can enable a gallery that appears at the end of the post. The gallery presents media in a Pinterest-style masonry layout with hover/click interactions for viewing descriptions and full-size media. Gallery metadata (descriptions, ordering) is defined in a JSON manifest file that lives alongside the media files, allowing the author to annotate auto-discovered content.

## Glossary

- **Gallery**: A masonry-style grid of images and videos displayed as an appendix section at the end of a blog post
- **Gallery_Button**: A prominent call-to-action element rendered at the end of the post content that navigates the reader to the gallery section
- **Gallery_Item**: A single image or video within the gallery, consisting of the media file and an optional one-line description
- **Gallery_Manifest**: A JSON file (`gallery.json`) placed inside a post's media folder that lists gallery items with their descriptions and display order
- **Masonry_Layout**: A grid layout where items are arranged in columns with varying heights, filling vertical space efficiently (Pinterest-style)
- **Lightbox**: A full-screen overlay that displays a single gallery item at its full size along with its description
- **Media_Folder**: A directory under `frontend/public/media/{folder-name}` containing images and videos for a specific post
- **Blog_Post**: A Markdown or MDX content file in `frontend/src/content/blog/` with frontmatter metadata
- **Content_Schema**: The Zod-based validation schema defined in `frontend/src/content/config.ts` that validates blog post frontmatter
- **Gallery_Init_Script**: A Node.js CLI script runnable via `npm run gallery:init` that scans a Media_Folder and generates a Gallery_Manifest skeleton file

## Requirements

### Requirement 1: Gallery Opt-In via Frontmatter

**User Story:** As a blog author, I want to enable a gallery on specific posts through frontmatter, so that only posts with behind-the-scenes content display a gallery.

#### Acceptance Criteria

1. THE Content_Schema SHALL include an optional `gallery` field of type string that specifies the Media_Folder name
2. WHEN the `gallery` frontmatter field is omitted or empty, THE Blog_Post SHALL render without any gallery section or Gallery_Button
3. WHEN the `gallery` frontmatter field contains a valid folder name, THE Blog_Post SHALL render the Gallery_Button and gallery section
4. THE Content_Schema SHALL validate that the `gallery` field, when provided, is a non-empty string

### Requirement 2: Gallery Manifest for Item Metadata

**User Story:** As a blog author, I want to define descriptions and ordering for gallery items in a JSON file, so that I can annotate auto-discovered media without modifying post content.

#### Acceptance Criteria

1. THE Gallery_Manifest SHALL be a JSON file named `gallery.json` located in the Media_Folder specified by the post's `gallery` frontmatter field
2. THE Gallery_Manifest SHALL contain an array of objects, each with a required `file` field (string, filename) and an optional `description` field (string, one-line caption)
3. WHEN a Gallery_Manifest exists, THE Gallery SHALL display items in the order defined in the manifest
4. WHEN a Gallery_Manifest exists, THE Gallery SHALL only display media files that are listed in the manifest (allowing the author to curate which files appear)
5. IF a Gallery_Manifest does not exist in the Media_Folder, THEN THE Gallery SHALL auto-discover all image and video files in the folder and display them sorted alphabetically by filename
6. THE Gallery SHALL support the following file extensions for images: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
7. THE Gallery SHALL support the following file extensions for videos: `.mp4`, `.webm`

### Requirement 3: Gallery Button at End of Post

**User Story:** As a reader, I want a clear visual cue at the end of a post to access the gallery, so that I can easily find and explore behind-the-scenes content.

#### Acceptance Criteria

1. WHEN a Blog_Post has a valid `gallery` frontmatter field, THE BlogPost layout SHALL render a Gallery_Button after the post content and before the post footer
2. THE Gallery_Button SHALL be a prominent, full-width clickable element with a label indicating gallery access (e.g., "View Gallery" or "Behind the Scenes")
3. WHEN clicked, THE Gallery_Button SHALL scroll the page to the gallery section
4. THE Gallery_Button SHALL be styled consistently with the site's existing design system (using CSS custom properties for colors, fonts, borders, and transitions)

### Requirement 4: Masonry Layout Gallery Display

**User Story:** As a reader, I want to browse gallery media in an attractive masonry grid, so that I can quickly scan through all the behind-the-scenes content.

#### Acceptance Criteria

1. THE Gallery SHALL render Gallery_Items in a Masonry_Layout with multiple columns
2. THE Masonry_Layout SHALL use CSS columns to arrange items, filling vertical space without uniform row heights
3. THE Masonry_Layout SHALL display 3 columns on desktop viewports (above 1024px), 2 columns on tablet viewports (641px–1024px), and 1 column on mobile viewports (640px and below)
4. WHEN a Gallery_Item is an image, THE Gallery SHALL render it as an `<img>` element with `loading="lazy"` for performance
5. WHEN a Gallery_Item is a video, THE Gallery SHALL render it as a `<video>` element with a visible poster frame or first-frame preview
6. THE Gallery SHALL display each Gallery_Item with rounded corners and consistent spacing matching the site's existing border-radius and gap patterns

### Requirement 5: Gallery Item Hover Interaction

**User Story:** As a reader, I want to see a short description when I hover over a gallery item, so that I can understand the context of each image or video before viewing it full-size.

#### Acceptance Criteria

1. WHEN a Gallery_Item has a description and the user hovers over the item, THE Gallery SHALL display the description as a text overlay on the item
2. THE description overlay SHALL use large, readable text styled consistently with the site's typography
3. THE description overlay SHALL appear with a semi-transparent background to maintain readability over the media
4. WHEN a Gallery_Item has no description, THE Gallery SHALL display no overlay on hover
5. WHEN the user moves the pointer away from the Gallery_Item, THE Gallery SHALL hide the description overlay

### Requirement 6: Lightbox Full-Size View

**User Story:** As a reader, I want to click on a gallery item to see it full-size with its description, so that I can view the media in detail.

#### Acceptance Criteria

1. WHEN the user clicks on a Gallery_Item, THE Gallery SHALL open a Lightbox overlay displaying the media at full size
2. WHEN the Gallery_Item is an image, THE Lightbox SHALL display the image scaled to fit the viewport while maintaining aspect ratio
3. WHEN the Gallery_Item is a video, THE Lightbox SHALL display the video with playback controls
4. WHEN the Gallery_Item has a description, THE Lightbox SHALL display the description below the media in large, readable text
5. THE Lightbox SHALL include a visible close button that dismisses the overlay
6. WHEN the user clicks outside the media content area or presses the Escape key, THE Lightbox SHALL close
7. THE Lightbox SHALL include navigation controls (previous/next) to browse between Gallery_Items without closing the overlay
8. THE Lightbox SHALL use a dark semi-transparent backdrop to focus attention on the media content

### Requirement 7: Responsive and Accessible Gallery

**User Story:** As a reader on any device, I want the gallery to be usable and accessible, so that I can enjoy the content regardless of my device or assistive technology.

#### Acceptance Criteria

1. THE Gallery SHALL be fully functional on mobile devices, with tap interactions replacing hover for description display
2. WHEN on a touch device, THE Gallery SHALL display the description overlay on first tap and open the Lightbox on second tap (or provide an explicit "view full size" action)
3. THE Gallery SHALL provide `alt` attributes on all image elements, using the Gallery_Item description when available or the filename as fallback
4. THE Lightbox SHALL trap keyboard focus while open, allowing Tab navigation between the close button, navigation controls, and media
5. THE Lightbox navigation controls SHALL be operable via keyboard arrow keys (left/right)
6. THE Gallery section SHALL include an appropriate heading (e.g., `<h2>`) for document structure and screen reader navigation

### Requirement 8: Gallery Visual Consistency

**User Story:** As a site owner, I want the gallery to match the existing site theme, so that the feature feels like a natural part of the site.

#### Acceptance Criteria

1. THE Gallery SHALL use the site's existing CSS custom properties (`--color-bg`, `--color-surface`, `--color-border`, `--color-text`, `--color-text-muted`, `--color-accent`, `--font-sans`, `--font-mono`, `--transition`)
2. THE Gallery SHALL render correctly in both dark and light color schemes as defined by the site's `prefers-color-scheme` media queries
3. THE Gallery section SHALL be visually separated from the post content with a border or spacing consistent with the post footer style


### Requirement 9: Gallery Manifest Initialization Script

**User Story:** As a blog author, I want to run a CLI command that auto-generates a gallery.json skeleton from a media folder, so that I do not have to manually list every file when setting up a new gallery.

#### Acceptance Criteria

1. THE Gallery_Init_Script SHALL be runnable via `npm run gallery:init -- {folder-name}`, where `{folder-name}` is the name of a directory under `frontend/public/media/`
2. WHEN executed, THE Gallery_Init_Script SHALL scan the specified Media_Folder for all files matching the supported image extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`) and video extensions (`.mp4`, `.webm`)
3. THE Gallery_Init_Script SHALL generate a `gallery.json` file in the specified Media_Folder containing a JSON array of objects, each with a `file` field set to the discovered filename and a `description` field set to an empty string
4. THE Gallery_Init_Script SHALL sort the generated entries alphabetically by filename
5. IF a `gallery.json` file already exists in the specified Media_Folder, THEN THE Gallery_Init_Script SHALL print a warning message to the console and exit without overwriting the existing file
6. IF the specified Media_Folder does not exist under `frontend/public/media/`, THEN THE Gallery_Init_Script SHALL print an error message indicating the folder was not found and exit with a non-zero exit code
7. IF no supported media files are found in the specified Media_Folder, THEN THE Gallery_Init_Script SHALL print a warning message indicating no supported files were found and exit without creating a `gallery.json` file
8. WHEN the Gallery_Init_Script successfully generates a `gallery.json` file, THE Gallery_Init_Script SHALL print a summary message listing the number of items added and the output file path
