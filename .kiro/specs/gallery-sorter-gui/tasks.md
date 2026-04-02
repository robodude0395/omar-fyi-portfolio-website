# Implementation Plan: Gallery Sorter GUI

## Overview

Build a single-file procedural Python script (`tools/gallery-sorter/gallery_sorter.py`) that provides a tkinter GUI for browsing media files, accepting/rejecting them, writing descriptions, and outputting a `gallery.json` manifest. Implementation proceeds bottom-up: pure logic functions first, then GUI construction, then wiring and documentation.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create `tools/gallery-sorter/` directory
  - Create `tools/gallery-sorter/requirements.txt` with `Pillow` and `opencv-python-headless`
  - Create `tools/gallery-sorter/gallery_sorter.py` with module docstring, imports (`sys`, `json`, `pathlib`, `tkinter`, `PIL`, `cv2`), and constants (`SUPPORTED_EXTENSIONS`, `IMAGE_EXTENSIONS`, `VIDEO_EXTENSIONS`)
  - Create `tools/gallery-sorter/tests/` directory (empty `__init__.py`)
  - _Requirements: 1.5_

- [x] 2. Implement manifest serialization and deserialization
  - [x] 2.1 Implement `serialize_manifest()` and `deserialize_manifest()`
    - `serialize_manifest(entries)` → JSON string with 2-space indent + trailing newline
    - `deserialize_manifest(json_string)` → list of `{"file", "description"}` dicts
    - _Requirements: 5.3, 5.6, 9.1_

  - [ ]* 2.2 Write property test: serialization round-trip
    - **Property 1: Serialization round-trip**
    - **Validates: Requirements 9.1, 6.1**
    - File: `tests/test_manifest.py`

  - [ ]* 2.3 Write property test: serialized manifest format
    - **Property 8: Serialized manifest format**
    - **Validates: Requirements 5.3, 5.6**
    - File: `tests/test_manifest.py`

- [x] 3. Implement media folder scanning and validation
  - [x] 3.1 Implement `resolve_media_root()` and `scan_media_folder()`
    - `resolve_media_root()` walks two levels up from script location to find `frontend/public/media/`
    - `scan_media_folder(folder_path)` returns sorted list of filenames with supported extensions (case-insensitive match)
    - _Requirements: 1.5, 1.6_

  - [ ]* 3.2 Write property test: scanner returns only supported files
    - **Property 2: Media scanner returns only supported files**
    - **Validates: Requirements 1.5**
    - File: `tests/test_scanner.py`

  - [ ]* 3.3 Write property test: non-existent folder produces error
    - **Property 3: Non-existent folder produces error**
    - **Validates: Requirements 1.4**
    - File: `tests/test_scanner.py`

- [x] 4. Implement manifest loading and state initialization
  - [x] 4.1 Implement `load_manifest()` and `init_file_states()`
    - `load_manifest(manifest_path)` → list of dicts from `gallery.json` (empty list if missing or invalid JSON)
    - `init_file_states(files, manifest)` → `(statuses_dict, descriptions_dict)`: manifest files → `"accepted"` with descriptions, others → `"undecided"`, stale entries → warning + skip
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 4.2 Write property test: manifest loading initializes file states correctly
    - **Property 9: Manifest loading initializes file states correctly**
    - **Validates: Requirements 6.2, 6.3, 6.4**
    - File: `tests/test_manifest.py`

  - [ ]* 4.3 Write property test: stale manifest entries are discarded
    - **Property 10: Stale manifest entries are discarded**
    - **Validates: Requirements 6.5**
    - File: `tests/test_manifest.py`

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement navigation, accept/reject, and progress logic
  - [x] 6.1 Implement `navigate()`, `accept_current()`, `reject_current()`, `format_progress()`
    - `navigate(state, direction)` clamps index to `[0, len(files)-1]`, saves description before moving
    - `accept_current(state)` sets status to `"accepted"`, advances to next
    - `reject_current(state)` sets status to `"rejected"`, advances to next
    - `format_progress(index, total)` returns `"{index+1} / {total}"`
    - _Requirements: 2.5, 2.6, 2.7, 2.8, 2.9, 3.3, 3.4, 3.6_

  - [ ]* 6.2 Write property test: navigation changes index correctly
    - **Property 4: Navigation changes index correctly**
    - **Validates: Requirements 2.6, 2.7, 2.8, 2.9**
    - File: `tests/test_navigation.py`

  - [ ]* 6.3 Write property test: accept and reject set correct status and advance
    - **Property 5: Accept and reject set correct status and advance**
    - **Validates: Requirements 3.3, 3.4, 3.6**
    - File: `tests/test_navigation.py`

  - [ ]* 6.4 Write property test: progress indicator formatting
    - **Property 6: Progress indicator formatting**
    - **Validates: Requirements 2.5**
    - File: `tests/test_navigation.py`

- [x] 7. Implement manifest building and saving
  - [x] 7.1 Implement `save_manifest()` and `save_manifest_to_disk()`
    - `save_manifest(state)` collects accepted files in file-list order, builds entries, prompts for overwrite if `gallery.json` exists, writes to disk
    - `save_manifest_to_disk(entries, manifest_path)` writes serialized JSON to file
    - _Requirements: 5.1, 5.2, 5.4, 5.5, 5.6, 5.7_

  - [ ]* 7.2 Write property test: manifest contains exactly accepted files in file-list order
    - **Property 7: Manifest contains exactly accepted files in file-list order**
    - **Validates: Requirements 5.4, 5.5**
    - File: `tests/test_manifest.py`

- [x] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Build the tkinter GUI
  - [x] 9.1 Implement `init_state()` and `build_gui()`
    - `init_state(folder_path, files, existing_manifest)` builds the full state dict
    - `build_gui(state)` creates the tkinter window: filename label, progress label, canvas, description entry, Accept/Reject/Prev/Next/Save buttons, shortcut hints footer
    - Store all widget references in the state dict
    - _Requirements: 2.1, 2.4, 2.5, 3.1, 3.2, 4.1, 5.1, 7.4_

  - [x] 9.2 Implement `bind_shortcuts()` and `update_ui()`
    - `bind_shortcuts(state)` binds `a`=Accept, `r`=Reject, `→`=Next, `←`=Prev, `Ctrl+S`=Save, `Space`=play/pause
    - `update_ui(state)` refreshes progress, filename, status color, description field, button enabled/disabled states
    - `save_current_description(state)` and `get_status_color(status)` helpers
    - _Requirements: 3.5, 4.2, 4.3, 4.4, 7.1, 7.2, 7.3, 7.4_

- [x] 10. Implement media display
  - [x] 10.1 Implement `show_current_file()`, `show_image()`, `show_gif()`, `show_video()`, `stop_playback()`
    - `show_current_file(state)` stops active playback, routes to correct display function by extension
    - `show_image(state, filepath)` loads with Pillow, scales to fit canvas, displays as PhotoImage
    - `show_gif(state, filepath)` extracts frames via ImageSequence, animates with `after()` scheduling
    - `show_video(state, filepath)` opens with cv2.VideoCapture, decodes frames at native FPS, renders via `after()`, Space toggles play/pause
    - `stop_playback(state)` cancels pending `after()` callback, releases VideoCapture
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 10.2 Write property test: description persistence across navigation
    - **Property 11: Description persistence across navigation**
    - **Validates: Requirements 4.3**
    - File: `tests/test_navigation.py`

- [x] 11. Implement CLI entry point and folder picker
  - [x] 11.1 Implement `main()` and `show_folder_picker()`
    - `main()` parses `sys.argv` for optional folder name, resolves media root, validates folder, launches GUI
    - `show_folder_picker(media_root)` shows tkinter Listbox dialog of available subfolders, returns selected name or None
    - Add `if __name__ == "__main__": main()` guard
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Write documentation
  - [x] 13.1 Create `tools/gallery-sorter/README.md`
    - Full documentation: purpose, installation (`pip install -r requirements.txt`), command-line usage (with and without folder argument), all features, keyboard shortcuts table, dependencies, `gallery.json` format
    - _Requirements: 8.3_

  - [x] 13.2 Add Gallery Sorter section to root `README.md`
    - Brief section (few paragraphs max) describing the tool's purpose and basic usage command
    - Direct reader to `tools/gallery-sorter/README.md` for full docs
    - _Requirements: 8.1, 8.2_

- [x] 14. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis with `@settings(max_examples=100)`
- All property tests tag format: `# Feature: gallery-sorter-gui, Property N: <name>`
- Tests import functions directly from `gallery_sorter.py`
- The script is procedural — no classes, state is a plain dict
