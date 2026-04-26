import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    /**
     * Hero image(s) displayed at the top of the post.
     * Pass a single string for one image, or an array of strings
     * to display multiple images side by side (great for portraits).
     */
    heroImage: z.union([z.string(), z.array(z.string())]).optional(),
    /**
     * Controls hero image sizing. Set to "contain" to cap the height
     * of portrait/tall images so they don't dominate the viewport.
     * Default behaviour (omitted or "cover") is unchanged.
     */
    heroFit: z.enum(["cover", "contain"]).default("cover"),
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

    /** Mark a post as featured to highlight it on the homepage. */
    featured: z.boolean().default(false),
    /**
     * Optional gallery folder name. When set, enables the gallery appendix.
     * Must match a directory name under frontend/public/media/.
     * Example: "worldskills"
     */
    gallery: z.string().min(1).optional(),
  }),
});

export const collections = { blog };
