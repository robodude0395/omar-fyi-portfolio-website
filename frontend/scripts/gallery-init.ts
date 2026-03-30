import { existsSync, readdirSync, writeFileSync } from "node:fs";
import { join, extname, resolve } from "node:path";

const SUPPORTED_EXTENSIONS = [
  ".jpg",
  ".jpeg",
  ".png",
  ".webp",
  ".gif",
  ".mp4",
  ".webm",
];

const folderName = process.argv[2];

if (!folderName) {
  console.error("Usage: npm run gallery:init -- <folder-name>");
  process.exit(1);
}

const mediaDir = resolve("public", "media", folderName);

if (!existsSync(mediaDir)) {
  console.error(`Error: folder not found → ${mediaDir}`);
  process.exit(1);
}

const manifestPath = join(mediaDir, "gallery.json");

if (existsSync(manifestPath)) {
  console.warn(`Warning: gallery.json already exists → ${manifestPath}`);
  process.exit(0);
}

const files = readdirSync(mediaDir)
  .filter((f) => SUPPORTED_EXTENSIONS.includes(extname(f).toLowerCase()))
  .sort((a, b) => a.localeCompare(b));

if (files.length === 0) {
  console.warn("Warning: no supported media files found in " + mediaDir);
  process.exit(0);
}

const entries = files.map((file) => ({ file, description: "" }));

writeFileSync(manifestPath, JSON.stringify(entries, null, 2) + "\n");

console.log(`${entries.length} items added → ${manifestPath}`);
