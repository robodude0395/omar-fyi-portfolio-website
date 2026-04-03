#!/usr/bin/env python3
"""Quick-and-dirty GUI to pick images for the About page hero gallery."""

from __future__ import annotations

import platform
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from urllib.parse import unquote

from PIL import Image, ImageTk

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
MEDIA_ROOT = REPO_ROOT / "frontend" / "public" / "media"
ABOUT_PAGE = REPO_ROOT / "frontend" / "src" / "pages" / "about.astro"

THUMB_SIZE = (160, 160)

# Markers used to locate the gallery block in about.astro
GALLERY_START = '<!-- ── Hero gallery ── -->'
GALLERY_OPEN = '<div class="gallery">'
GALLERY_CLOSE_MARKER = '</div>\n\n    <div class="about-content">'


def media_rel(path: Path) -> str:
    """Return /media/... web path for a file inside public/media."""
    return "/" + path.relative_to(MEDIA_ROOT.parent).as_posix()


def build_gallery_html(items: list[dict]) -> str:
    """Build the inner HTML for the gallery div."""
    lines: list[str] = []
    for item in items:
        lines.append(
            f'      <div class="gallery-item">\n'
            f'        <img src="{item["src"]}" alt="{item["alt"]}" loading="lazy" />\n'
            f"      </div>"
        )
    return "\n" + "\n".join(lines) + "\n    "


def _find_gallery_block(text: str) -> tuple[int, int] | None:
    """Return (start, end) indices of the gallery inner HTML.

    start = index right after '<div class="gallery">'
    end   = index of the closing '</div>' that ends the gallery block
    """
    comment_idx = text.find(GALLERY_START)
    if comment_idx == -1:
        return None
    open_idx = text.find(GALLERY_OPEN, comment_idx)
    if open_idx == -1:
        return None
    inner_start = open_idx + len(GALLERY_OPEN)

    # Find the closing </div> that sits right before <div class="about-content">
    close_idx = text.find(GALLERY_CLOSE_MARKER, inner_start)
    if close_idx == -1:
        return None
    return inner_start, close_idx


def parse_existing_gallery() -> list[dict]:
    """Read the current about.astro and pull out existing gallery items."""
    text = ABOUT_PAGE.read_text()
    bounds = _find_gallery_block(text)
    if not bounds:
        return []
    inner = text[bounds[0]:bounds[1]]
    items: list[dict] = []
    for img in re.finditer(r'src="([^"]+)"[^>]*alt="([^"]*)"', inner):
        items.append({"src": img.group(1), "alt": img.group(2)})
    return items


def write_gallery(items: list[dict]) -> None:
    """Overwrite the gallery block in about.astro."""
    text = ABOUT_PAGE.read_text()
    bounds = _find_gallery_block(text)
    if not bounds:
        raise RuntimeError("Could not locate gallery block in about.astro")
    new_inner = build_gallery_html(items)
    new_text = text[:bounds[0]] + new_inner + text[bounds[1]:]
    ABOUT_PAGE.write_text(new_text)


# ── GUI ────────────────────────────────────────────────────────────────────────

class HeroGalleryPicker:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Hero Gallery Picker")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        self.items: list[dict] = parse_existing_gallery()
        self.thumb_refs: list[ImageTk.PhotoImage] = []  # prevent GC

        self._build_ui()
        self._refresh_list()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Top button bar
        bar = tk.Frame(self.root)
        bar.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Button(bar, text="Add Images…", command=self._add_images).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(bar, text="Move Up", command=self._move_up).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="Move Down", command=self._move_down).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="Save to about.astro", command=self._save, bg="#4CAF50", fg="white").pack(side=tk.RIGHT)

        # Scrollable list area
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel (platform-aware)
        if platform.system() == "Darwin":
            self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-e.delta, "units"))
        else:
            self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

        # Status bar
        self.status_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.status_var, anchor=tk.W).pack(fill=tk.X, padx=10, pady=(0, 8))

    # ── List rendering ─────────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.thumb_refs.clear()
        self.row_widgets: list[dict] = []

        for i, item in enumerate(self.items):
            row = tk.Frame(self.scroll_frame, bd=1, relief=tk.RIDGE, padx=6, pady=4)
            row.pack(fill=tk.X, pady=2, padx=2)

            # Selection checkbox
            var = tk.BooleanVar(value=False)
            tk.Checkbutton(row, variable=var).pack(side=tk.LEFT, padx=(0, 6))

            # Thumbnail
            thumb_label = tk.Label(row, width=THUMB_SIZE[0], height=THUMB_SIZE[1])
            thumb_label.pack(side=tk.LEFT, padx=(0, 10))
            self._load_thumb(thumb_label, item["src"])

            # Info area
            info = tk.Frame(row)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(info, text=item["src"], anchor=tk.W, font=("monospace", 11)).pack(fill=tk.X)

            alt_frame = tk.Frame(info)
            alt_frame.pack(fill=tk.X, pady=(4, 0))
            tk.Label(alt_frame, text="Alt:").pack(side=tk.LEFT)
            alt_entry = tk.Entry(alt_frame)
            alt_entry.insert(0, item["alt"])
            alt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

            self.row_widgets.append({"var": var, "alt_entry": alt_entry, "index": i})

        self.status_var.set(f"{len(self.items)} image(s) in gallery")

    def _load_thumb(self, label: tk.Label, src: str) -> None:
        """Try to load a thumbnail from the public/media path."""
        try:
            # src is like /media/sigma-labs/Sigma_Patagonia.jpg
            file_path = MEDIA_ROOT.parent / src.lstrip("/")
            if not file_path.exists():
                label.config(text="(not found)", width=20)
                return
            img = Image.open(file_path)
            img.thumbnail(THUMB_SIZE)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, width=THUMB_SIZE[0], height=THUMB_SIZE[1])
            self.thumb_refs.append(photo)
        except Exception:
            label.config(text="(error)", width=20)

    # ── Actions ────────────────────────────────────────────────────────────

    def _sync_alts(self) -> None:
        """Sync alt text from entries back into self.items."""
        for rw in self.row_widgets:
            self.items[rw["index"]]["alt"] = rw["alt_entry"].get()

    def _add_images(self) -> None:
        self._sync_alts()
        paths = filedialog.askopenfilenames(
            title="Select images for hero gallery",
            initialdir=str(MEDIA_ROOT),
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.gif *.JPG *.JPEG *.PNG")],
        )
        if not paths:
            return
        for p in paths:
            path = Path(p)
            try:
                src = media_rel(path)
            except ValueError:
                messagebox.showwarning("Outside media", f"{path.name} is not inside public/media — skipping.")
                continue
            # Skip duplicates
            if any(item["src"] == src for item in self.items):
                continue
            self.items.append({"src": src, "alt": path.stem.replace("-", " ").replace("_", " ")})
        self._refresh_list()

    def _get_selected_indices(self) -> list[int]:
        return sorted([rw["index"] for rw in self.row_widgets if rw["var"].get()])

    def _move_up(self) -> None:
        self._sync_alts()
        sel = self._get_selected_indices()
        if not sel or sel[0] == 0:
            return
        for i in sel:
            self.items[i - 1], self.items[i] = self.items[i], self.items[i - 1]
        self._refresh_list()

    def _move_down(self) -> None:
        self._sync_alts()
        sel = self._get_selected_indices()
        if not sel or sel[-1] >= len(self.items) - 1:
            return
        for i in reversed(sel):
            self.items[i + 1], self.items[i] = self.items[i], self.items[i + 1]
        self._refresh_list()

    def _remove_selected(self) -> None:
        self._sync_alts()
        sel = self._get_selected_indices()
        if not sel:
            return
        for i in reversed(sel):
            self.items.pop(i)
        self._refresh_list()

    def _save(self) -> None:
        self._sync_alts()
        if not self.items:
            messagebox.showwarning("Empty", "Gallery is empty — nothing to save.")
            return
        try:
            write_gallery(self.items)
            self.status_var.set(f"Saved {len(self.items)} image(s) to about.astro ✓")
            messagebox.showinfo("Saved", f"Wrote {len(self.items)} gallery items to about.astro")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main() -> None:
    root = tk.Tk()
    HeroGalleryPicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
