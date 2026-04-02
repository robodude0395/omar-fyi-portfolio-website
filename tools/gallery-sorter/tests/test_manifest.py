"""Unit tests for manifest loading and state initialization."""

import json
import pytest
from pathlib import Path

# Import functions under test
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gallery_sorter import load_manifest, init_file_states, save_manifest_to_disk, save_manifest


# ---------------------------------------------------------------------------
# load_manifest tests
# ---------------------------------------------------------------------------


class TestLoadManifest:
    """Tests for load_manifest()."""

    def test_missing_file_returns_empty(self, tmp_path):
        """Missing gallery.json returns empty list."""
        result = load_manifest(tmp_path / "gallery.json")
        assert result == []

    def test_valid_manifest(self, tmp_path):
        """Valid gallery.json is parsed correctly."""
        manifest = [
            {"file": "a.jpg", "description": "Photo A"},
            {"file": "b.mp4", "description": ""},
        ]
        path = tmp_path / "gallery.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = load_manifest(path)
        assert result == manifest

    def test_invalid_json_returns_empty(self, tmp_path, capsys):
        """Invalid JSON prints warning and returns empty list."""
        path = tmp_path / "gallery.json"
        path.write_text("{not valid json", encoding="utf-8")
        result = load_manifest(path)
        assert result == []
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "invalid JSON" in captured.out

    def test_non_array_json_returns_empty(self, tmp_path, capsys):
        """JSON that isn't an array prints warning and returns empty list."""
        path = tmp_path / "gallery.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = load_manifest(path)
        assert result == []
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_malformed_entry_missing_keys_skipped(self, tmp_path, capsys):
        """Entries missing required keys are skipped with a warning."""
        manifest = [
            {"file": "a.jpg", "description": "ok"},
            {"file": "b.jpg"},  # missing description
            {"description": "orphan"},  # missing file
            {"file": "c.jpg", "description": "also ok"},
        ]
        path = tmp_path / "gallery.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = load_manifest(path)
        assert len(result) == 2
        assert result[0] == {"file": "a.jpg", "description": "ok"}
        assert result[1] == {"file": "c.jpg", "description": "also ok"}
        captured = capsys.readouterr()
        assert captured.out.count("Warning") == 2

    def test_non_dict_entries_skipped(self, tmp_path, capsys):
        """Non-dict entries in the array are skipped with a warning."""
        manifest = [
            {"file": "a.jpg", "description": "ok"},
            "just a string",
            42,
        ]
        path = tmp_path / "gallery.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = load_manifest(path)
        assert len(result) == 1
        assert result[0] == {"file": "a.jpg", "description": "ok"}

    def test_empty_array(self, tmp_path):
        """Empty JSON array returns empty list."""
        path = tmp_path / "gallery.json"
        path.write_text("[]", encoding="utf-8")
        result = load_manifest(path)
        assert result == []


# ---------------------------------------------------------------------------
# init_file_states tests
# ---------------------------------------------------------------------------


class TestInitFileStates:
    """Tests for init_file_states()."""

    def test_all_files_in_manifest(self):
        """All files present in manifest are marked accepted with descriptions."""
        files = ["a.jpg", "b.png"]
        manifest = [
            {"file": "a.jpg", "description": "Photo A"},
            {"file": "b.png", "description": "Photo B"},
        ]
        statuses, descriptions = init_file_states(files, manifest)
        assert statuses == {"a.jpg": "accepted", "b.png": "accepted"}
        assert descriptions == {"a.jpg": "Photo A", "b.png": "Photo B"}

    def test_no_manifest(self):
        """Empty manifest means all files are undecided."""
        files = ["a.jpg", "b.png", "c.mp4"]
        statuses, descriptions = init_file_states(files, [])
        for f in files:
            assert statuses[f] == "undecided"
            assert descriptions[f] == ""

    def test_partial_manifest(self):
        """Files in manifest are accepted, others are undecided."""
        files = ["a.jpg", "b.png", "c.mp4"]
        manifest = [{"file": "b.png", "description": "middle one"}]
        statuses, descriptions = init_file_states(files, manifest)
        assert statuses["a.jpg"] == "undecided"
        assert statuses["b.png"] == "accepted"
        assert statuses["c.mp4"] == "undecided"
        assert descriptions["b.png"] == "middle one"
        assert descriptions["a.jpg"] == ""

    def test_stale_entries_skipped(self, capsys):
        """Manifest entries for files not on disk are skipped with a warning."""
        files = ["a.jpg"]
        manifest = [
            {"file": "a.jpg", "description": "exists"},
            {"file": "deleted.png", "description": "gone"},
        ]
        statuses, descriptions = init_file_states(files, manifest)
        assert "deleted.png" not in statuses
        assert "deleted.png" not in descriptions
        assert statuses["a.jpg"] == "accepted"
        captured = capsys.readouterr()
        assert "deleted.png" in captured.out
        assert "Warning" in captured.out

    def test_every_file_has_entry(self):
        """Every file in the input list has an entry in both dicts."""
        files = ["x.jpg", "y.mp4", "z.gif"]
        manifest = [{"file": "y.mp4", "description": "video"}]
        statuses, descriptions = init_file_states(files, manifest)
        assert set(statuses.keys()) == set(files)
        assert set(descriptions.keys()) == set(files)

    def test_empty_files_and_manifest(self):
        """Empty inputs produce empty dicts."""
        statuses, descriptions = init_file_states([], [])
        assert statuses == {}
        assert descriptions == {}


# ---------------------------------------------------------------------------
# save_manifest_to_disk tests
# ---------------------------------------------------------------------------


class TestSaveManifestToDisk:
    """Tests for save_manifest_to_disk()."""

    def test_writes_json_file(self, tmp_path):
        """Writes a valid JSON file with 2-space indent and trailing newline."""
        entries = [
            {"file": "a.jpg", "description": "Photo A"},
            {"file": "b.mp4", "description": ""},
        ]
        manifest_path = tmp_path / "gallery.json"
        save_manifest_to_disk(entries, manifest_path)

        text = manifest_path.read_text(encoding="utf-8")
        assert text.endswith("\n")
        parsed = json.loads(text)
        assert parsed == entries

    def test_empty_entries(self, tmp_path):
        """Empty entries list writes an empty JSON array."""
        manifest_path = tmp_path / "gallery.json"
        save_manifest_to_disk([], manifest_path)

        text = manifest_path.read_text(encoding="utf-8")
        assert json.loads(text) == []

    def test_overwrites_existing_file(self, tmp_path):
        """Overwrites an existing gallery.json without prompting."""
        manifest_path = tmp_path / "gallery.json"
        manifest_path.write_text("old content", encoding="utf-8")

        entries = [{"file": "new.jpg", "description": "new"}]
        save_manifest_to_disk(entries, manifest_path)

        parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert parsed == entries


# ---------------------------------------------------------------------------
# save_manifest tests
# ---------------------------------------------------------------------------


class TestSaveManifest:
    """Tests for save_manifest()."""

    def _make_state(self, tmp_path, files, statuses, descriptions):
        """Helper to build a minimal state dict for testing."""
        return {
            "folder_path": tmp_path,
            "files": files,
            "statuses": statuses,
            "descriptions": descriptions,
            "current_index": 0,
            "desc_entry": None,  # No GUI widget in tests
            "root": None,
        }

    def test_only_accepted_files_saved(self, tmp_path):
        """Only accepted files appear in the output manifest."""
        files = ["a.jpg", "b.png", "c.mp4"]
        statuses = {"a.jpg": "accepted", "b.png": "rejected", "c.mp4": "accepted"}
        descriptions = {"a.jpg": "Photo A", "b.png": "", "c.mp4": "Video C"}
        state = self._make_state(tmp_path, files, statuses, descriptions)

        save_manifest(state)

        manifest_path = tmp_path / "gallery.json"
        parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert len(parsed) == 2
        assert parsed[0] == {"file": "a.jpg", "description": "Photo A"}
        assert parsed[1] == {"file": "c.mp4", "description": "Video C"}

    def test_preserves_file_list_order(self, tmp_path):
        """Accepted files appear in the same order as state['files']."""
        files = ["z.jpg", "a.png", "m.mp4"]
        statuses = {"z.jpg": "accepted", "a.png": "accepted", "m.mp4": "accepted"}
        descriptions = {"z.jpg": "Z", "a.png": "A", "m.mp4": "M"}
        state = self._make_state(tmp_path, files, statuses, descriptions)

        save_manifest(state)

        parsed = json.loads((tmp_path / "gallery.json").read_text(encoding="utf-8"))
        assert [e["file"] for e in parsed] == ["z.jpg", "a.png", "m.mp4"]

    def test_no_accepted_files_writes_empty_array(self, tmp_path):
        """Zero accepted files writes an empty JSON array."""
        files = ["a.jpg", "b.png"]
        statuses = {"a.jpg": "rejected", "b.png": "undecided"}
        descriptions = {"a.jpg": "", "b.png": ""}
        state = self._make_state(tmp_path, files, statuses, descriptions)

        save_manifest(state)

        parsed = json.loads((tmp_path / "gallery.json").read_text(encoding="utf-8"))
        assert parsed == []

    def test_empty_description_preserved(self, tmp_path):
        """Accepted files with empty descriptions get empty string in manifest."""
        files = ["a.jpg"]
        statuses = {"a.jpg": "accepted"}
        descriptions = {"a.jpg": ""}
        state = self._make_state(tmp_path, files, statuses, descriptions)

        save_manifest(state)

        parsed = json.loads((tmp_path / "gallery.json").read_text(encoding="utf-8"))
        assert parsed[0]["description"] == ""

    def test_output_format(self, tmp_path):
        """Output uses 2-space indentation and trailing newline."""
        files = ["a.jpg"]
        statuses = {"a.jpg": "accepted"}
        descriptions = {"a.jpg": "test"}
        state = self._make_state(tmp_path, files, statuses, descriptions)

        save_manifest(state)

        text = (tmp_path / "gallery.json").read_text(encoding="utf-8")
        assert text.endswith("\n")
        assert "  " in text  # 2-space indent present
