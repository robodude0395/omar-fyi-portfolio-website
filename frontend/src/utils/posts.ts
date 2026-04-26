import { getCollection } from "astro:content";

/** Returns all blog posts sorted by date (newest first). */
export async function getPublishedPosts() {
  return (await getCollection("blog"))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}

/** Returns up to `limit` featured published posts (newest first). */
export async function getFeaturedPosts(limit = 3) {
  return (await getPublishedPosts())
    .filter((post) => post.data.featured)
    .slice(0, limit);
}
