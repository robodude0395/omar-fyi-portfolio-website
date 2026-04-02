# Gallery Sorter GUI

A standalone graphical tool for visually browsing media files in a blog post's media folder, accepting or rejecting each for inclusion, writing descriptions, and outputting a `gallery.json` manifest.

No more guessing what `IMG-20250626-WA0023.jpg` looks like.

## Dependencies

- Python 3.10+
- [Pillow](https://pypi.org/project/Pillow/) — image loading and GIF animation
- [opencv-python-headless](https://pypi.org/project/opencv-python-headless/) — video playback (mp4, webm)
- tkinter — ships with Python (no install needed on most systems)

## Installation

```bash
cd tools/gallery-sorter
pip install -r requirements.txt
```

## Usage

Open a specific media folder:

```bash
python gallery_sorter.py Flight-Motion-Platform-Part-1-Final-Project
```

Or launch without arguments to get a folder picker dialog:

```bash
python gallery_sorter.py
```

The folder name corresponds to a subdirectory under `frontend/public/media/`.

## Features

- Browse images (jpg, jpeg, png, webp) and animated GIFs rendered in the GUI
- Play videos (mp4, webm) directly in the tool with play/pause support
- Accept or reject each file for inclusion in `gallery.json`
- Write a description caption for each accepted file
- Load an existing `gallery.json` to resume editing (accepted files and descriptions are pre-populated)
- Overwrite confirmation when saving over an existing manifest
- Progress indicator showing current position in the file list

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `a` | Accept current file |
| `r` | Reject current file |
| `→` (Right) | Next file |
| `←` (Left) | Previous file |
| `Ctrl+S` | Save manifest |
| `Space` | Play/pause video |

Shortcuts for `a` and `r` are disabled while typing in the description field.

## gallery.json Format

The output is a JSON array written to the media folder:

```json
[
  { "file": "IMG_001.jpg", "description": "Soldering the main PCB" },
  { "file": "demo.mp4", "description": "" }
]
```

Only accepted files are included, in the order they appear in the file list. The description can be empty.

## How It Works

1. The tool scans the selected media folder for supported files (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.mp4`, `.webm`)
2. If a `gallery.json` already exists, files listed in it are pre-marked as accepted with their descriptions
3. You flip through each file, viewing the actual image or video
4. Accept or reject each one — accepted files get a description field
5. Hit Save (or `Ctrl+S`) to write `gallery.json` to the folder
6. The blog post's gallery section picks up the manifest automatically
