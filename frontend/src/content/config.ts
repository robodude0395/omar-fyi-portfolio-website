import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
    /**
     * Thumbnail image displayed in the blog listing page.
     * Should be a path relative to the `public/` directory (e.g. "/media/my-thumb.jpg").
     * Recommended size: 200×200px or similar square/landscape ratio.
     * If omitted, a default placeholder thumbnail is shown (src/assets/images/thumbnal-default.png).
     *
     * Example usage in frontmatter:
     *   thumbnail: "/media/my-thumbnail.jpg"
     */
    thumbnail: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    /**
     * Optional gallery folder name. When set, enables the gallery appendix.
     * Must match a directory name under frontend/public/media/.
     * Example: "worldskills"
     */
    gallery: z.string().min(1).optional(),
  }),
});

export const collections = { blog };
