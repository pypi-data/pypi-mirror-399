"""Tests for input utilities."""

import json
import tempfile
from pathlib import Path

import pytest

from yoinkr.utils.input import URLSource


class TestURLSource:
    """Tests for URLSource."""

    def test_from_list(self):
        """Test reading from list."""
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "  https://example.com/3  ",  # With whitespace
            "# comment",  # Should be skipped
            "",  # Empty line
        ]

        result = list(URLSource.from_list(urls))

        assert len(result) == 3
        assert result[0] == "https://example.com/1"
        assert result[2] == "https://example.com/3"

    def test_from_string(self):
        """Test reading from string."""
        text = """https://example.com/1
https://example.com/2
# comment
https://example.com/3"""

        result = list(URLSource.from_string(text))

        assert len(result) == 3

    def test_from_txt_file(self):
        """Test reading from .txt file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://example.com/1\n")
            f.write("https://example.com/2\n")
            f.write("# comment\n")
            f.write("https://example.com/3\n")
            path = f.name

        try:
            result = list(URLSource.from_file(path))

            assert len(result) == 3
            assert result[0] == "https://example.com/1"
        finally:
            Path(path).unlink()

    def test_from_csv_file(self):
        """Test reading from .csv file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("url,name\n")
            f.write("https://example.com/1,Page 1\n")
            f.write("https://example.com/2,Page 2\n")
            path = f.name

        try:
            result = list(URLSource.from_file(path))

            assert len(result) == 2
            assert result[0] == "https://example.com/1"
        finally:
            Path(path).unlink()

    def test_from_csv_file_with_column(self):
        """Test reading from .csv with specific column."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,link,extra\n")
            f.write("Page 1,https://example.com/1,foo\n")
            f.write("Page 2,https://example.com/2,bar\n")
            path = f.name

        try:
            result = list(URLSource.from_file(path, column="link"))

            assert len(result) == 2
            assert result[0] == "https://example.com/1"
        finally:
            Path(path).unlink()

    def test_from_json_file_list(self):
        """Test reading from .json file with list of URLs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                [
                    "https://example.com/1",
                    "https://example.com/2",
                ],
                f,
            )
            path = f.name

        try:
            result = list(URLSource.from_file(path))

            assert len(result) == 2
        finally:
            Path(path).unlink()

    def test_from_json_file_objects(self):
        """Test reading from .json file with list of objects."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                [
                    {"url": "https://example.com/1", "name": "Page 1"},
                    {"url": "https://example.com/2", "name": "Page 2"},
                ],
                f,
            )
            path = f.name

        try:
            result = list(URLSource.from_file(path))

            assert len(result) == 2
            assert result[0] == "https://example.com/1"
        finally:
            Path(path).unlink()

    def test_from_json_file_with_urls_key(self):
        """Test reading from .json file with 'urls' key."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "urls": [
                        "https://example.com/1",
                        "https://example.com/2",
                    ]
                },
                f,
            )
            path = f.name

        try:
            result = list(URLSource.from_file(path))

            assert len(result) == 2
        finally:
            Path(path).unlink()

    def test_count(self):
        """Test counting URLs in file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://example.com/1\n")
            f.write("https://example.com/2\n")
            f.write("https://example.com/3\n")
            path = f.name

        try:
            count = URLSource.count(path)
            assert count == 3
        finally:
            Path(path).unlink()

    def test_validate_url(self):
        """Test URL validation."""
        assert URLSource.validate_url("https://example.com") is True
        assert URLSource.validate_url("http://example.com") is True
        assert URLSource.validate_url("example.com") is False
        assert URLSource.validate_url("ftp://example.com") is False
