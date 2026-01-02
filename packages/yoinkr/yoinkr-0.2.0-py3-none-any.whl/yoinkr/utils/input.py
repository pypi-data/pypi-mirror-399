"""File-based URL input utilities."""

import csv
import json
from pathlib import Path
from typing import Iterator, Optional, Union


class URLSource:
    """Source for URLs to scrape."""

    @staticmethod
    def from_file(
        file_path: Union[str, Path],
        column: Optional[str] = None,
        skip_header: bool = True,
    ) -> Iterator[str]:
        """
        Read URLs from a file.

        Supports:
            - .txt: One URL per line
            - .csv: URLs in specified column or first column
            - .json: List of URLs or objects with 'url' key

        Args:
            file_path: Path to the file
            column: Column name for CSV files
            skip_header: Whether to skip header in CSV files

        Yields:
            URL strings
        """
        path = Path(file_path)

        if path.suffix == ".txt":
            yield from URLSource._read_txt(path)

        elif path.suffix == ".csv":
            yield from URLSource._read_csv(path, column, skip_header)

        elif path.suffix == ".json":
            yield from URLSource._read_json(path)

        else:
            # Try as plain text
            yield from URLSource._read_txt(path)

    @staticmethod
    def from_list(urls: list[str]) -> Iterator[str]:
        """
        Iterate over list of URLs.

        Args:
            urls: List of URL strings

        Yields:
            URL strings (stripped and non-empty)
        """
        for url in urls:
            url = url.strip()
            if url and not url.startswith("#"):
                yield url

    @staticmethod
    def from_string(text: str) -> Iterator[str]:
        """
        Parse URLs from a string (one per line).

        Args:
            text: String containing URLs (one per line)

        Yields:
            URL strings
        """
        for line in text.split("\n"):
            url = line.strip()
            if url and not url.startswith("#"):
                yield url

    @staticmethod
    def _read_txt(path: Path) -> Iterator[str]:
        """Read URLs from a text file."""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith("#"):
                    yield url

    @staticmethod
    def _read_csv(path: Path, column: Optional[str], skip_header: bool) -> Iterator[str]:
        """Read URLs from a CSV file."""
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            col_idx = 0
            if skip_header:
                header = next(reader, None)
                if column and header:
                    try:
                        col_idx = header.index(column)
                    except ValueError:
                        col_idx = 0

            for row in reader:
                if row and len(row) > col_idx:
                    url = row[col_idx].strip()
                    if url:
                        yield url

    @staticmethod
    def _read_json(path: Path) -> Iterator[str]:
        """Read URLs from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    yield item
                elif isinstance(item, dict) and "url" in item:
                    yield item["url"]

        elif isinstance(data, dict) and "urls" in data:
            for url in data["urls"]:
                if isinstance(url, str):
                    yield url
                elif isinstance(url, dict) and "url" in url:
                    yield url["url"]

    @staticmethod
    def count(file_path: Union[str, Path]) -> int:
        """
        Count URLs in a file without loading all into memory.

        Args:
            file_path: Path to the file

        Returns:
            Number of URLs in the file
        """
        return sum(1 for _ in URLSource.from_file(file_path))

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Basic URL validation.

        Args:
            url: URL string to validate

        Returns:
            True if URL appears valid
        """
        url = url.strip().lower()
        return url.startswith(("http://", "https://"))
