"""Unit tests for I/O utilities."""

import json
import tempfile
from pathlib import Path

import pytest

from scale_align.io import (
    format_alignment,
    format_indices,
    get_output_filename,
    load_classification,
    load_correspondence,
    write_alignment,
)
from scale_align.selection import AlignmentMatch


class TestLoadClassification:
    """Tests for load_classification function."""

    def test_loads_lines(self, tmp_path):
        """Test loading lines from file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Line 1\nLine 2\nLine 3\n")

        result = load_classification(str(file_path))

        assert result == ["Line 1", "Line 2", "Line 3"]

    def test_strips_whitespace(self, tmp_path):
        """Test that whitespace is stripped."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("  Line 1  \n\nLine 2\n")

        result = load_classification(str(file_path))

        assert result == ["Line 1", "Line 2"]

    def test_raises_file_not_found(self):
        """Test FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_classification("/nonexistent/path.txt")


class TestLoadCorrespondence:
    """Tests for load_correspondence function."""

    def test_loads_json(self, tmp_path):
        """Test loading correspondence from JSON."""
        file_path = tmp_path / "corr.json"
        data = [["A", "A"], ["A0111", "A01.11"]]
        file_path.write_text(json.dumps(data))

        result = load_correspondence(str(file_path))

        assert result == [("A", "A"), ("A0111", "A01.11")]

    def test_raises_on_invalid_format(self, tmp_path):
        """Test ValueError on invalid format."""
        file_path = tmp_path / "corr.json"
        file_path.write_text(json.dumps({"not": "a list"}))

        with pytest.raises(ValueError):
            load_correspondence(str(file_path))


class TestFormatIndices:
    """Tests for format_indices function."""

    def test_empty_list(self):
        assert format_indices([]) == "[]"

    def test_single_index(self):
        assert format_indices([0]) == "[0]"

    def test_multiple_indices(self):
        assert format_indices([1, 2, 3]) == "[1,2,3]"


class TestFormatAlignment:
    """Tests for format_alignment function."""

    def test_one_to_one(self):
        match = AlignmentMatch([0], [1], 0.95)
        assert format_alignment(match) == "[0]:[1]:0.95"

    def test_one_to_many(self):
        match = AlignmentMatch([0], [1, 2], 0.87)
        assert format_alignment(match) == "[0]:[1,2]:0.87"

    def test_no_match(self):
        match = AlignmentMatch([3], [], 0.0)
        assert format_alignment(match) == "[3]:[]:0.0"


class TestGetOutputFilename:
    """Tests for get_output_filename function."""

    def test_simple_codes(self):
        assert get_output_filename("A0111", "A01.11") == "A0111_A01.11.txt"

    def test_sanitizes_slashes(self):
        assert get_output_filename("A/B", "C\\D") == "A_B_C_D.txt"


class TestWriteAlignment:
    """Tests for write_alignment function."""

    def test_writes_file(self, tmp_path):
        """Test writing alignment to file."""
        output_path = tmp_path / "output.txt"
        alignments = [
            AlignmentMatch([0], [0, 1], 0.87),
            AlignmentMatch([1], [2], 0.92),
        ]

        write_alignment(str(output_path), alignments)

        content = output_path.read_text()
        lines = content.strip().split("\n")
        assert lines[0] == "[0]:[0,1]:0.87"
        assert lines[1] == "[1]:[2]:0.92"
