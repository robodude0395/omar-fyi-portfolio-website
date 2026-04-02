"""Gallery Sorter GUI — a standalone tkinter tool for browsing media files,
accepting or rejecting each for inclusion, writing descriptions, and outputting
a gallery.json manifest.

Usage:
    python gallery_sorter.py [folder_name]

If folder_name is provided, opens that subfolder under frontend/public/media/.
Otherwise, shows a folder picker dialog.
"""

import sys
import json
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence, ImageOps

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".webm"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | {".gif"}


# ---------------------------------------------------------------------------
# Manifest Serialization / Deserialization
# ---------------------------------------------------------------------------


def serialize_manifest(entries: list[dict]) -> str:
    """Serialize list of {"file", "description"} dicts to JSON string with 2-space indent + trailing newline."""
    return json.dumps(entries, indent=2) + "\n"


def deserialize_manifest(json_string: str) -> list[dict]:
    """Parse JSON string into list of {"file", "description"} dicts."""
    return json.loads(json_string)


# ---------------------------------------------------------------------------
# Media Folder Resolution & Scanning
# ---------------------------------------------------------------------------


def resolve_media_root() -> Path:
    """Walk two levels up from script location to find frontend/public/media/."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    return project_root / "frontend" / "public" / "media"


def scan_media_folder(folder_path: Path) -> list[str]:
    """Return sorted list of supported media filenames. Case-insensitive extension match."""
    files = [
        f.name for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        raise ValueError(f"No supported media files found in {folder_path}")
    return sorted(files)


# ---------------------------------------------------------------------------
# Manifest Loading & State Initialization
# ---------------------------------------------------------------------------


def load_manifest(manifest_path: Path) -> list[dict]:
    """Load gallery.json, return list of {"file": ..., "description": ...} dicts."""
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Warning: invalid JSON in {manifest_path}: {exc}")
        return []
    if not isinstance(data, list):
        print(f"Warning: expected JSON array in {manifest_path}, got {type(data).__name__}")
        return []
    entries: list[dict] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"Warning: skipping non-dict entry at index {i} in {manifest_path}")
            continue
        if "file" not in item or "description" not in item:
            print(f"Warning: skipping malformed entry at index {i} in {manifest_path} (missing keys)")
            continue
        entries.append({"file": item["file"], "description": item["description"]})
    return entries


def init_file_states(files: list[str], manifest: list[dict]) -> tuple[dict, dict]:
    """Build per-file status and description dicts from a file list and manifest."""
    file_set = set(files)
    statuses: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    manifest_files_on_disk: set[str] = set()
    for entry in manifest:
        fname = entry["file"]
        if fname not in file_set:
            print(f"Warning: manifest references '{fname}' which no longer exists on disk — skipping")
            continue
        manifest_files_on_disk.add(fname)
        statuses[fname] = "accepted"
        descriptions[fname] = entry["description"]
    for fname in files:
        if fname not in manifest_files_on_disk:
            statuses[fname] = "undecided"
            descriptions[fname] = ""
    return statuses, descriptions


# ---------------------------------------------------------------------------
# Navigation, Accept/Reject, and Progress
# ---------------------------------------------------------------------------


def save_current_description(state: dict) -> None:
    """Read description from the desc_entry widget and store it for the current file."""
    widget = state.get("desc_entry")
    if widget is None:
        return
    current_file = state["files"][state["current_index"]]
    state["descriptions"][current_file] = widget.get().strip()


def navigate(state: dict, direction: int) -> None:
    """Move current_index by direction (+1 or -1), clamped to valid range."""
    save_current_description(state)
    new_index = state["current_index"] + direction
    state["current_index"] = max(0, min(new_index, len(state["files"]) - 1))


def accept_current(state: dict) -> None:
    """Mark current file as accepted, save description, advance."""
    current_file = state["files"][state["current_index"]]
    state["statuses"][current_file] = "accepted"
    save_current_description(state)
    state["current_index"] = min(state["current_index"] + 1, len(state["files"]) - 1)


def reject_current(state: dict) -> None:
    """Mark current file as rejected, advance."""
    current_file = state["files"][state["current_index"]]
    state["statuses"][current_file] = "rejected"
    state["current_index"] = min(state["current_index"] + 1, len(state["files"]) - 1)


def format_progress(index: int, total: int) -> str:
    """Return a human-readable progress string, e.g. '3 / 15'."""
    return f"{index + 1} / {total}"


# ---------------------------------------------------------------------------
# Manifest Building & Saving
# ---------------------------------------------------------------------------


def save_manifest_to_disk(entries: list[dict], manifest_path: Path) -> None:
    """Write serialized manifest to disk."""
    manifest_path.write_text(serialize_manifest(entries), encoding="utf-8")


def save_manifest(state: dict) -> None:
    """Collect accepted files in file-list order and write to disk."""
    save_current_description(state)
    entries: list[dict] = []
    for filename in state["files"]:
        if state["statuses"].get(filename) == "accepted":
            entries.append({
                "file": filename,
                "description": state["descriptions"].get(filename, ""),
            })
    save_manifest_to_disk(entries, state["folder_path"] / "gallery.json")


# ---------------------------------------------------------------------------
# State Initialization
# ---------------------------------------------------------------------------


def init_state(folder_path: Path, files: list[str], existing_manifest: list[dict]) -> dict:
    """Build the full application state dict."""
    statuses, descriptions = init_file_states(files, existing_manifest)
    return {
        "folder_path": folder_path,
        "files": files,
        "statuses": statuses,
        "descriptions": descriptions,
        "current_index": 0,
        "playback_id": None,       # after() callback ID for GIF animation
        "video_process": None,      # subprocess for system video player
        # Widget references — set by build_gui
        "root": None, "canvas": None, "desc_entry": None,
        "status_label": None, "progress_label": None, "filename_label": None,
        "accept_btn": None, "reject_btn": None,
        "prev_btn": None, "next_btn": None, "save_btn": None,
        "_photo_ref": None,
    }


# ---------------------------------------------------------------------------
# GUI Construction
# ---------------------------------------------------------------------------


def build_gui(state: dict) -> None:
    """Create the tkinter window and all widgets."""
    folder_name = state["folder_path"].name
    root = tk.Tk()
    root.title(f"Gallery Sorter \u2014 {folder_name}")
    root.geometry("900x700")
    state["root"] = root

    # Top bar
    top = tk.Frame(root)
    top.pack(fill=tk.X, padx=8, pady=(8, 0))
    state["filename_label"] = tk.Label(top, text="", anchor=tk.W, font=("TkDefaultFont", 11))
    state["filename_label"].pack(side=tk.LEFT, fill=tk.X, expand=True)
    state["progress_label"] = tk.Label(top, text="", anchor=tk.E, font=("TkDefaultFont", 11))
    state["progress_label"].pack(side=tk.RIGHT)

    # Canvas
    state["canvas"] = tk.Canvas(root, bg="white", highlightthickness=0)
    state["canvas"].pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    # Info bar
    info = tk.Frame(root)
    info.pack(fill=tk.X, padx=8, pady=(0, 4))
    state["status_label"] = tk.Label(info, text="UNDECIDED", fg="grey", font=("TkDefaultFont", 10, "bold"))
    state["status_label"].pack(anchor=tk.W)
    desc_frame = tk.Frame(info)
    desc_frame.pack(fill=tk.X)
    tk.Label(desc_frame, text="Description:").pack(side=tk.LEFT)
    state["desc_entry"] = tk.Entry(desc_frame)
    state["desc_entry"].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    # Buttons
    btns = tk.Frame(root)
    btns.pack(fill=tk.X, padx=8, pady=(0, 4))
    state["prev_btn"] = tk.Button(btns, text="Prev")
    state["prev_btn"].pack(side=tk.LEFT, padx=(0, 4))
    state["accept_btn"] = tk.Button(btns, text="Accept")
    state["accept_btn"].pack(side=tk.LEFT, padx=(0, 4))
    state["reject_btn"] = tk.Button(btns, text="Reject")
    state["reject_btn"].pack(side=tk.LEFT, padx=(0, 4))
    state["next_btn"] = tk.Button(btns, text="Next")
    state["next_btn"].pack(side=tk.LEFT)
    state["save_btn"] = tk.Button(btns, text="Save")
    state["save_btn"].pack(side=tk.RIGHT)

    # Footer
    tk.Label(
        root, text="Shortcuts: a=Accept  r=Reject  \u2190\u2192=Navigate  Ctrl+S=Save  Space=Play video",
        font=("TkDefaultFont", 9), fg="grey",
    ).pack(fill=tk.X, padx=8, pady=(0, 8))

    # Wire buttons
    state["prev_btn"].config(command=lambda: (navigate(state, -1), show_current_file(state)))
    state["accept_btn"].config(command=lambda: (accept_current(state), show_current_file(state)))
    state["reject_btn"].config(command=lambda: (reject_current(state), show_current_file(state)))
    state["next_btn"].config(command=lambda: (navigate(state, +1), show_current_file(state)))
    state["save_btn"].config(command=lambda: save_manifest_with_confirm(state))


# ---------------------------------------------------------------------------
# UI Helpers
# ---------------------------------------------------------------------------


def get_status_color(status: str) -> str:
    if status == "accepted":
        return "#2e7d32"
    elif status == "rejected":
        return "#c62828"
    return "#757575"


def update_ui(state: dict) -> None:
    """Refresh all UI elements based on current state."""
    files = state["files"]
    idx = state["current_index"]
    current_file = files[idx]
    state["progress_label"].config(text=format_progress(idx, len(files)))
    state["filename_label"].config(text=current_file)
    status = state["statuses"].get(current_file, "undecided")
    state["status_label"].config(text=status.upper(), fg=get_status_color(status))
    desc_entry = state["desc_entry"]
    desc_entry.config(state=tk.NORMAL)
    desc_entry.delete(0, tk.END)
    desc_entry.insert(0, state["descriptions"].get(current_file, ""))
    state["prev_btn"].config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
    state["next_btn"].config(state=tk.NORMAL if idx < len(files) - 1 else tk.DISABLED)


# ---------------------------------------------------------------------------
# Playback Control
# ---------------------------------------------------------------------------


def stop_playback(state: dict) -> None:
    """Cancel any pending GIF animation callback. Kill any external video player."""
    if state["playback_id"] is not None:
        state["root"].after_cancel(state["playback_id"])
        state["playback_id"] = None
    proc = state.get("video_process")
    if proc is not None:
        proc.terminate()
        state["video_process"] = None


def open_video_in_system_player(state: dict, filepath: Path) -> None:
    """Open a video file in the system's default media player."""
    # Kill any previously opened player
    proc = state.get("video_process")
    if proc is not None:
        proc.terminate()
    try:
        state["video_process"] = subprocess.Popen(["open", str(filepath)])
    except FileNotFoundError:
        # Fallback for Linux
        try:
            state["video_process"] = subprocess.Popen(["xdg-open", str(filepath)])
        except FileNotFoundError:
            print(f"Warning: could not open {filepath} — no system player found")


# ---------------------------------------------------------------------------
# Media Display
# ---------------------------------------------------------------------------


def show_current_file(state: dict) -> None:
    """Stop active playback, route to correct display function, update UI."""
    stop_playback(state)
    update_ui(state)
    files = state["files"]
    if not files:
        return
    filename = files[state["current_index"]]
    ext = Path(filename).suffix.lower()
    filepath = state["folder_path"] / filename
    if ext in IMAGE_EXTENSIONS:
        show_image(state, filepath)
    elif ext == ".gif":
        show_gif(state, filepath)
    elif ext in VIDEO_EXTENSIONS:
        show_video_thumbnail(state, filepath)


def show_image(state: dict, filepath: Path) -> None:
    """Load image with Pillow, apply EXIF rotation, scale to fit canvas."""
    canvas = state["canvas"]
    canvas.delete("all")
    canvas.update_idletasks()
    cw, ch = canvas.winfo_width(), canvas.winfo_height()
    if cw < 10 or ch < 10:
        cw, ch = 800, 500
    try:
        img = Image.open(filepath)
        img = ImageOps.exif_transpose(img)
        iw, ih = img.size
        scale = min(cw / iw, ch / ih, 1.0)
        img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        state["_photo_ref"] = photo
        canvas.create_image(cw // 2, ch // 2, image=photo, anchor=tk.CENTER)
    except Exception as e:
        canvas.create_text(cw // 2, ch // 2, text=f"Error loading image:\n{e}", fill="red")


def show_gif(state: dict, filepath: Path) -> None:
    """Load animated GIF, extract frames, animate with after() scheduling."""
    canvas = state["canvas"]
    canvas.delete("all")
    canvas.update_idletasks()
    cw, ch = canvas.winfo_width(), canvas.winfo_height()
    if cw < 10 or ch < 10:
        cw, ch = 800, 500
    try:
        gif = Image.open(filepath)
        frames, durations = [], []
        try:
            while True:
                frame = gif.copy()
                iw, ih = frame.size
                scale = min(cw / iw, ch / ih, 1.0)
                frame = frame.resize((max(1, int(iw * scale)), max(1, int(ih * scale))), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame.convert("RGBA")))
                durations.append(gif.info.get("duration", 100))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        if not frames:
            return
        frame_index = [0]

        def animate():
            idx = frame_index[0]
            state["_photo_ref"] = frames[idx]
            canvas.delete("all")
            canvas.create_image(cw // 2, ch // 2, image=frames[idx], anchor=tk.CENTER)
            frame_index[0] = (idx + 1) % len(frames)
            state["playback_id"] = state["root"].after(max(durations[idx], 20), animate)

        animate()
    except Exception as e:
        canvas.create_text(cw // 2, ch // 2, text=f"Error loading GIF:\n{e}", fill="red")


def show_video_thumbnail(state: dict, filepath: Path) -> None:
    """Show a video thumbnail with a play button overlay. Space or click opens system player."""
    canvas = state["canvas"]
    canvas.delete("all")
    canvas.update_idletasks()
    cw, ch = canvas.winfo_width(), canvas.winfo_height()
    if cw < 10 or ch < 10:
        cw, ch = 800, 500

    # Draw video icon and instructions
    canvas.create_text(
        cw // 2, ch // 2 - 30,
        text="\u25B6",  # play triangle
        font=("TkDefaultFont", 72), fill="#444",
    )
    canvas.create_text(
        cw // 2, ch // 2 + 40,
        text=f"{filepath.name}\n\nPress Space or click to open in system player",
        font=("TkDefaultFont", 13), fill="#666", justify=tk.CENTER,
    )

    # Click canvas to play
    def on_click(event):
        open_video_in_system_player(state, filepath)

    canvas.bind("<Button-1>", on_click)
    # Store filepath for space key handler
    state["_current_video_path"] = filepath


# ---------------------------------------------------------------------------
# Keyboard Shortcuts
# ---------------------------------------------------------------------------


def bind_shortcuts(state: dict) -> None:
    """Bind keyboard shortcuts to the root window."""
    root = state["root"]

    def _accept(event):
        if event.widget == state["desc_entry"]:
            return
        accept_current(state)
        show_current_file(state)

    def _reject(event):
        if event.widget == state["desc_entry"]:
            return
        reject_current(state)
        show_current_file(state)

    def _next(event):
        navigate(state, +1)
        show_current_file(state)

    def _prev(event):
        navigate(state, -1)
        show_current_file(state)

    def _save(event):
        save_manifest_with_confirm(state)

    def _space(event):
        if event.widget == state["desc_entry"]:
            return
        vpath = state.get("_current_video_path")
        if vpath:
            open_video_in_system_player(state, vpath)

    root.bind("a", _accept)
    root.bind("r", _reject)
    root.bind("<Right>", _next)
    root.bind("<Left>", _prev)
    root.bind("<Control-s>", _save)
    root.bind("<space>", _space)


def save_manifest_with_confirm(state: dict) -> None:
    """Save manifest with overwrite confirmation."""
    manifest_path = state["folder_path"] / "gallery.json"
    if manifest_path.exists():
        if not messagebox.askyesno("Overwrite?", f"gallery.json already exists in {state['folder_path'].name}. Overwrite?"):
            return
    save_manifest(state)
    messagebox.showinfo("Saved", f"gallery.json saved to {state['folder_path'].name}")


# ---------------------------------------------------------------------------
# Folder Picker Dialog
# ---------------------------------------------------------------------------


def show_folder_picker(media_root: Path) -> str | None:
    """Show a tkinter Listbox dialog of available media subfolders."""
    folders = sorted([d.name for d in media_root.iterdir() if d.is_dir() and not d.name.startswith(".")])
    if not folders:
        print("Error: no media folders found under", media_root, file=sys.stderr)
        return None
    selected = [None]
    picker = tk.Tk()
    picker.title("Gallery Sorter \u2014 Select Folder")
    picker.geometry("400x500")
    tk.Label(picker, text="Select a media folder:", font=("TkDefaultFont", 12)).pack(pady=(10, 5))
    listbox = tk.Listbox(picker, font=("TkDefaultFont", 11))
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    for f in folders:
        listbox.insert(tk.END, f)

    def on_open():
        sel = listbox.curselection()
        if sel:
            selected[0] = folders[sel[0]]
            picker.destroy()

    listbox.bind("<Double-1>", lambda e: on_open())
    btns = tk.Frame(picker)
    btns.pack(fill=tk.X, padx=10, pady=10)
    tk.Button(btns, text="Open", command=on_open).pack(side=tk.RIGHT)
    tk.Button(btns, text="Cancel", command=picker.destroy).pack(side=tk.RIGHT, padx=(0, 5))
    picker.mainloop()
    return selected[0]


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def main():
    media_root = resolve_media_root()
    if not media_root.is_dir():
        print(f"Error: media root not found at {media_root}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
        folder_path = media_root / folder_name
        if not folder_path.is_dir():
            print(f"Error: folder '{folder_name}' not found under {media_root}", file=sys.stderr)
            sys.exit(1)
    else:
        folder_name = show_folder_picker(media_root)
        if folder_name is None:
            sys.exit(0)
        folder_path = media_root / folder_name

    try:
        files = scan_media_folder(folder_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    manifest = load_manifest(folder_path / "gallery.json")
    state = init_state(folder_path, files, manifest)
    build_gui(state)
    bind_shortcuts(state)
    show_current_file(state)
    state["root"].mainloop()


if __name__ == "__main__":
    main()
