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
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import cv2

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
    media_root = project_root / "frontend" / "public" / "media"
    return media_root


def scan_media_folder(folder_path: Path) -> list[str]:
    """Return sorted list of supported media filenames. Case-insensitive extension match.

    Raises ValueError if no supported files are found.
    """
    files = [
        f.name
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        raise ValueError(
            f"No supported media files found in {folder_path}"
        )
    return sorted(files)

# ---------------------------------------------------------------------------
# Manifest Loading & State Initialization
# ---------------------------------------------------------------------------


def load_manifest(manifest_path: Path) -> list[dict]:
    """Load gallery.json, return list of {"file": ..., "description": ...} dicts.

    Returns an empty list if the file is missing or contains invalid JSON.
    Skips malformed entries (missing "file" or "description" keys) with a warning.
    """
    if not manifest_path.exists():
        return []
    try:
        text = manifest_path.read_text(encoding="utf-8")
        data = json.loads(text)
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


def init_file_states(
    files: list[str], manifest: list[dict]
) -> tuple[dict, dict]:
    """Build per-file status and description dicts from a file list and manifest.

    Returns (statuses_dict, descriptions_dict):
      - Files present in the manifest → "accepted" with their description.
      - Files on disk but not in the manifest → "undecided" with empty description.
      - Manifest entries referencing files not in *files* → warning printed, skipped.
    """
    file_set = set(files)
    statuses: dict[str, str] = {}
    descriptions: dict[str, str] = {}

    # Track which manifest files are on disk
    manifest_files_on_disk: set[str] = set()

    for entry in manifest:
        fname = entry["file"]
        if fname not in file_set:
            print(f"Warning: manifest references '{fname}' which no longer exists on disk — skipping")
            continue
        manifest_files_on_disk.add(fname)
        statuses[fname] = "accepted"
        descriptions[fname] = entry["description"]

    # Files not in manifest → undecided
    for fname in files:
        if fname not in manifest_files_on_disk:
            statuses[fname] = "undecided"
            descriptions[fname] = ""

    return statuses, descriptions




# ---------------------------------------------------------------------------
# Navigation, Accept/Reject, and Progress
# ---------------------------------------------------------------------------


def save_current_description(state: dict) -> None:
    """Read description from the desc_entry widget and store it for the current file.

    No-op if desc_entry is None (e.g. during headless testing).
    """
    widget = state.get("desc_entry")
    if widget is None:
        return
    current_file = state["files"][state["current_index"]]
    state["descriptions"][current_file] = widget.get().strip()


def navigate(state: dict, direction: int) -> None:
    """Move current_index by *direction* (+1 or -1), clamped to [0, len(files)-1].

    Saves the current description before moving.
    Does NOT call show_current_file — GUI wiring is added later.
    """
    save_current_description(state)
    new_index = state["current_index"] + direction
    new_index = max(0, min(new_index, len(state["files"]) - 1))
    state["current_index"] = new_index


def accept_current(state: dict) -> None:
    """Mark the current file as 'accepted', save its description, and advance to the next file.

    Index is clamped at the last file.
    """
    current_file = state["files"][state["current_index"]]
    state["statuses"][current_file] = "accepted"
    save_current_description(state)
    new_index = state["current_index"] + 1
    new_index = min(new_index, len(state["files"]) - 1)
    state["current_index"] = new_index


def reject_current(state: dict) -> None:
    """Mark the current file as 'rejected' and advance to the next file.

    Index is clamped at the last file.
    """
    current_file = state["files"][state["current_index"]]
    state["statuses"][current_file] = "rejected"
    new_index = state["current_index"] + 1
    new_index = min(new_index, len(state["files"]) - 1)
    state["current_index"] = new_index


def format_progress(index: int, total: int) -> str:
    """Return a human-readable progress string, e.g. '3 / 15'."""
    return f"{index + 1} / {total}"


# ---------------------------------------------------------------------------
# Manifest Building & Saving
# ---------------------------------------------------------------------------


def save_manifest_to_disk(entries: list[dict], manifest_path: Path) -> None:
    """Write serialized manifest to disk using serialize_manifest()."""
    manifest_path.write_text(serialize_manifest(entries), encoding="utf-8")

# ---------------------------------------------------------------------------
# State Initialization
# ---------------------------------------------------------------------------


def init_state(folder_path: Path, files: list[str], existing_manifest: list[dict]) -> dict:
    """Build the full application state dict.

    Calls init_file_states() to derive per-file statuses and descriptions
    from the file list and any existing manifest data.
    """
    statuses, descriptions = init_file_states(files, existing_manifest)
    return {
        "folder_path": folder_path,
        "files": files,
        "statuses": statuses,
        "descriptions": descriptions,
        "current_index": 0,
        "playback_id": None,
        "video_capture": None,
        "video_playing": False,
        # Widget references — set by build_gui
        "root": None,
        "canvas": None,
        "desc_entry": None,
        "status_label": None,
        "progress_label": None,
        "filename_label": None,
        "accept_btn": None,
        "reject_btn": None,
        "prev_btn": None,
        "next_btn": None,
        "save_btn": None,
        "_photo_ref": None,  # prevent GC of PhotoImage
    }


# ---------------------------------------------------------------------------
# GUI Construction
# ---------------------------------------------------------------------------


def build_gui(state: dict) -> None:
    """Create the tkinter window and all widgets. Store widget references in state dict.

    Layout (top to bottom):
      - Top bar: filename label (left) + progress label (right)
      - Center: canvas for media display (expandable, white background)
      - Info bar: status label + description entry
      - Button bar: Prev, Accept, Reject, Next (left) and Save (right)
      - Footer: keyboard shortcut hints
    """
    folder_name = state["folder_path"].name

    root = tk.Tk()
    root.title(f"Gallery Sorter \u2014 {folder_name}")
    root.geometry("900x700")
    state["root"] = root

    # --- Top bar ---
    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, padx=8, pady=(8, 0))

    filename_label = tk.Label(top_frame, text="", anchor=tk.W, font=("TkDefaultFont", 11))
    filename_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    state["filename_label"] = filename_label

    progress_label = tk.Label(top_frame, text="", anchor=tk.E, font=("TkDefaultFont", 11))
    progress_label.pack(side=tk.RIGHT)
    state["progress_label"] = progress_label

    # --- Canvas (center, expandable) ---
    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
    state["canvas"] = canvas

    # --- Info bar: status + description ---
    info_frame = tk.Frame(root)
    info_frame.pack(fill=tk.X, padx=8, pady=(0, 4))

    status_label = tk.Label(info_frame, text="UNDECIDED", fg="grey", font=("TkDefaultFont", 10, "bold"))
    status_label.pack(anchor=tk.W)
    state["status_label"] = status_label

    desc_frame = tk.Frame(info_frame)
    desc_frame.pack(fill=tk.X)

    tk.Label(desc_frame, text="Description:").pack(side=tk.LEFT)
    desc_entry = tk.Entry(desc_frame)
    desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
    state["desc_entry"] = desc_entry

    # --- Button bar ---
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, padx=8, pady=(0, 4))

    prev_btn = tk.Button(btn_frame, text="Prev")
    prev_btn.pack(side=tk.LEFT, padx=(0, 4))
    state["prev_btn"] = prev_btn

    accept_btn = tk.Button(btn_frame, text="Accept")
    accept_btn.pack(side=tk.LEFT, padx=(0, 4))
    state["accept_btn"] = accept_btn

    reject_btn = tk.Button(btn_frame, text="Reject")
    reject_btn.pack(side=tk.LEFT, padx=(0, 4))
    state["reject_btn"] = reject_btn

    next_btn = tk.Button(btn_frame, text="Next")
    next_btn.pack(side=tk.LEFT)
    state["next_btn"] = next_btn

    save_btn = tk.Button(btn_frame, text="Save")
    save_btn.pack(side=tk.RIGHT)
    state["save_btn"] = save_btn

    # --- Footer: shortcut hints ---
    footer = tk.Label(
        root,
        text="Shortcuts: a=Accept  r=Reject  \u2190\u2192=Navigate  Ctrl+S=Save",
        font=("TkDefaultFont", 9),
        fg="grey",
    )
    footer.pack(fill=tk.X, padx=8, pady=(0, 8))

    # --- Wire up button commands ---
    prev_btn.config(command=lambda: (navigate(state, -1), show_current_file(state)))
    accept_btn.config(command=lambda: (accept_current(state), show_current_file(state)))
    reject_btn.config(command=lambda: (reject_current(state), show_current_file(state)))
    next_btn.config(command=lambda: (navigate(state, +1), show_current_file(state)))
    save_btn.config(command=lambda: save_manifest_with_confirm(state))


# ---------------------------------------------------------------------------
# UI Helpers
# ---------------------------------------------------------------------------


def get_status_color(status: str) -> str:
    """Return a color string: green for accepted, red for rejected, grey for undecided."""
    if status == "accepted":
        return "#2e7d32"  # green
    elif status == "rejected":
        return "#c62828"  # red
    return "#757575"  # grey


def update_ui(state: dict) -> None:
    """Refresh all UI elements based on current state.

    Updates progress label, filename label, status indicator, description field,
    and button enabled/disabled states.
    """
    files = state["files"]
    idx = state["current_index"]
    current_file = files[idx]

    # Progress label
    state["progress_label"].config(text=format_progress(idx, len(files)))

    # Filename label
    state["filename_label"].config(text=current_file)

    # Status label
    status = state["statuses"].get(current_file, "undecided")
    state["status_label"].config(text=status.upper(), fg=get_status_color(status))

    # Description entry
    desc_entry = state["desc_entry"]
    desc_entry.config(state=tk.NORMAL)
    desc_entry.delete(0, tk.END)
    desc_entry.insert(0, state["descriptions"].get(current_file, ""))
    if status != "accepted":
        desc_entry.config(state=tk.DISABLED)

    # Button states
    state["prev_btn"].config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
    state["next_btn"].config(state=tk.NORMAL if idx < len(files) - 1 else tk.DISABLED)
    state["accept_btn"].config(state=tk.NORMAL)
    state["reject_btn"].config(state=tk.NORMAL)


def stop_playback(state: dict) -> None:
    """Cancel any pending after() callback. Release VideoCapture if open."""
    if state["playback_id"] is not None:
        state["root"].after_cancel(state["playback_id"])
        state["playback_id"] = None
    if state["video_capture"] is not None:
        state["video_capture"].release()
        state["video_capture"] = None
    state["video_playing"] = False


def show_current_file(state: dict) -> None:
    """Stop any active playback, then route to the correct display function
    based on the current file's extension. Update UI labels and button states."""
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
        show_video(state, filepath)


def show_image(state: dict, filepath: Path) -> None:
    """Load image with Pillow, scale to fit canvas, display as PhotoImage."""
    canvas = state["canvas"]
    canvas.delete("all")
    canvas.update_idletasks()
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()
    if cw < 10 or ch < 10:
        cw, ch = 800, 500
    try:
        img = Image.open(filepath)
        iw, ih = img.size
        scale = min(cw / iw, ch / ih, 1.0)  # don't upscale
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        state["_photo_ref"] = photo  # prevent GC
        canvas.create_image(cw // 2, ch // 2, image=photo, anchor=tk.CENTER)
    except Exception as e:
        canvas.create_text(cw // 2, ch // 2, text=f"Error loading image:\n{e}", fill="red")


def show_gif(state: dict, filepath: Path) -> None:
    """Load GIF with Pillow, extract all frames, animate using after() scheduling."""
    canvas = state["canvas"]
    canvas.delete("all")
    canvas.update_idletasks()
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()
    if cw < 10 or ch < 10:
        cw, ch = 800, 500
    try:
        gif = Image.open(filepath)
        # Extract all frames
        frames = []
        durations = []
        try:
            while True:
                frame = gif.copy()
                iw, ih = frame.size
                scale = min(cw / iw, ch / ih, 1.0)
                new_w = max(1, int(iw * scale))
                new_h = max(1, int(ih * scale))
                frame = frame.resize((new_w, new_h), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame.convert("RGBA")))
                durations.append(gif.info.get("duration", 100))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        if not frames:
            return

        frame_index = [0]  # mutable container for closure

        def animate():
            idx = frame_index[0]
            state["_photo_ref"] = frames[idx]
            canvas.delete("all")
            canvas.create_image(cw // 2, ch // 2, image=frames[idx], anchor=tk.CENTER)
            frame_index[0] = (idx + 1) % len(frames)
            delay = max(durations[idx], 20)  # minimum 20ms
            state["playback_id"] = state["root"].after(delay, animate)

        animate()
    except Exception as e:
        canvas.create_text(cw // 2, ch // 2, text=f"Error loading GIF:\n{e}", fill="red")


def show_video(state: dict, filepath: Path) -> None:
    """Open with cv2.VideoCapture, decode frames at native FPS, render via after()."""
    canvas = state["canvas"]
    canvas.delete("all")
    try:
        cap = cv2.VideoCapture(str(filepath))
        if not cap.isOpened():
            canvas.create_text(400, 300, text=f"Error: cannot open video\n{filepath.name}", fill="red")
            return
        state["video_capture"] = cap
        state["video_playing"] = True

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 24
        delay_ms = max(int(1000 / fps), 10)

        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 800, 500

        def next_frame():
            if not state["video_playing"]:
                return
            cap = state["video_capture"]
            if cap is None:
                return
            ret, frame = cap.read()
            if not ret:
                # Loop: seek back to start
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    return
            # Convert BGR → RGB → PIL → PhotoImage
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            iw, ih = img.size
            scale = min(cw / iw, ch / ih, 1.0)
            new_w = max(1, int(iw * scale))
            new_h = max(1, int(ih * scale))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            state["_photo_ref"] = photo
            canvas.delete("all")
            canvas.create_image(cw // 2, ch // 2, image=photo, anchor=tk.CENTER)
            state["playback_id"] = state["root"].after(delay_ms, next_frame)

        next_frame()
    except Exception as e:
        canvas.create_text(400, 300, text=f"Error playing video:\n{e}", fill="red")


def toggle_video_playback(state: dict) -> None:
    """Toggle video play/pause."""
    if state["video_capture"] is None:
        return  # not viewing a video
    if state["video_playing"]:
        # Pause
        state["video_playing"] = False
        if state["playback_id"] is not None:
            state["root"].after_cancel(state["playback_id"])
            state["playback_id"] = None
    else:
        # Resume
        state["video_playing"] = True
        show_video_resume(state)


def show_video_resume(state: dict) -> None:
    """Resume video playback from current position."""
    cap = state["video_capture"]
    if cap is None:
        return
    canvas = state["canvas"]
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 24
    delay_ms = max(int(1000 / fps), 10)
    canvas.update_idletasks()
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()
    if cw < 10 or ch < 10:
        cw, ch = 800, 500

    def next_frame():
        if not state["video_playing"]:
            return
        cap = state["video_capture"]
        if cap is None:
            return
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        iw, ih = img.size
        scale = min(cw / iw, ch / ih, 1.0)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        state["_photo_ref"] = photo
        canvas.delete("all")
        canvas.create_image(cw // 2, ch // 2, image=photo, anchor=tk.CENTER)
        state["playback_id"] = state["root"].after(delay_ms, next_frame)

    next_frame()


def bind_shortcuts(state: dict) -> None:
    """Bind keyboard shortcuts to the root window.

    Shortcuts:
      a → Accept current file
      r → Reject current file
      Right → Next file
      Left → Previous file
      Ctrl+S → Save manifest
      Space → Toggle video playback
    """
    root = state["root"]

    def _accept(event: tk.Event) -> None:
        if event.widget == state["desc_entry"]:
            return
        accept_current(state)
        show_current_file(state)

    def _reject(event: tk.Event) -> None:
        if event.widget == state["desc_entry"]:
            return
        reject_current(state)
        show_current_file(state)

    def _next(event: tk.Event) -> None:
        navigate(state, +1)
        show_current_file(state)

    def _prev(event: tk.Event) -> None:
        navigate(state, -1)
        show_current_file(state)

    def _save(event: tk.Event) -> None:
        save_manifest(state)

    def _toggle_playback(event: tk.Event) -> None:
        toggle_video_playback(state)

    root.bind("a", _accept)
    root.bind("r", _reject)
    root.bind("<Right>", _next)
    root.bind("<Left>", _prev)
    root.bind("<Control-s>", _save)
    root.bind("<space>", _toggle_playback)


def save_manifest_with_confirm(state: dict) -> None:
    """Save manifest with overwrite confirmation if gallery.json already exists."""
    manifest_path = state["folder_path"] / "gallery.json"
    if manifest_path.exists():
        if not messagebox.askyesno(
            "Overwrite?",
            f"gallery.json already exists in {state['folder_path'].name}. Overwrite?",
        ):
            return
    save_manifest(state)
    messagebox.showinfo("Saved", f"gallery.json saved to {state['folder_path'].name}")


def save_manifest(state: dict) -> None:
    """Collect accepted files in file-list order, build manifest entries, and write to disk.

    Steps:
      1. Save the current description from the entry widget.
      2. Iterate state["files"] in order; for each accepted file, add an entry.
      3. Write to gallery.json in the media folder via save_manifest_to_disk().

    Note: overwrite confirmation prompt is wired in the GUI task.
    """
    save_current_description(state)

    entries: list[dict] = []
    for filename in state["files"]:
        if state["statuses"].get(filename) == "accepted":
            entries.append({
                "file": filename,
                "description": state["descriptions"].get(filename, ""),
            })

    manifest_path = state["folder_path"] / "gallery.json"
    save_manifest_to_disk(entries, manifest_path)



# ---------------------------------------------------------------------------
# Folder Picker Dialog
# ---------------------------------------------------------------------------


def show_folder_picker(media_root: Path) -> str | None:
    """Show a tkinter Listbox dialog of available media subfolders. Returns folder name or None."""
    folders = sorted([
        d.name for d in media_root.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])
    if not folders:
        print("Error: no media folders found under", media_root, file=sys.stderr)
        return None

    selected = [None]  # mutable container for closure

    picker = tk.Tk()
    picker.title("Gallery Sorter — Select Folder")
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

    def on_double_click(event):
        on_open()

    listbox.bind("<Double-1>", on_double_click)

    btn_frame = tk.Frame(picker)
    btn_frame.pack(fill=tk.X, padx=10, pady=10)
    tk.Button(btn_frame, text="Open", command=on_open).pack(side=tk.RIGHT)
    tk.Button(btn_frame, text="Cancel", command=picker.destroy).pack(side=tk.RIGHT, padx=(0, 5))

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

    # Parse optional folder name argument
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
        folder_path = media_root / folder_name
        if not folder_path.is_dir():
            print(f"Error: folder '{folder_name}' not found under {media_root}", file=sys.stderr)
            sys.exit(1)
    else:
        folder_name = show_folder_picker(media_root)
        if folder_name is None:
            sys.exit(0)  # user cancelled
        folder_path = media_root / folder_name

    # Scan for media files
    try:
        files = scan_media_folder(folder_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Load existing manifest
    manifest = load_manifest(folder_path / "gallery.json")

    # Build state and launch GUI
    state = init_state(folder_path, files, manifest)
    build_gui(state)
    bind_shortcuts(state)
    show_current_file(state)
    state["root"].mainloop()


if __name__ == "__main__":
    main()
