"""JSONPath extraction method."""

import json
import re
from typing import TYPE_CHECKING, Any, Union

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class JSONPathMethod(BaseMethod):
    """
    Extract data from JSON using JSONPath expressions.

    Supports a subset of JSONPath syntax:
        - $.field - Root field access
        - $.field.nested - Nested field access
        - $.array[0] - Array index access
        - $.array[*] - All array elements
        - $.array[*].field - Field from all array elements
        - $..field - Recursive descent (find field at any level)

    Examples:
        Instruction("title", "$.data.title", method="jsonpath")
        Instruction("prices", "$.products[*].price", method="jsonpath", multiple=True)
        Instruction("all_names", "$..name", method="jsonpath", multiple=True)
    """

    @property
    def name(self) -> str:
        """Method identifier."""
        return "jsonpath"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """
        Execute JSONPath extraction.

        Args:
            source: JSON string, dict, or HTML containing JSON
            instruction: Extraction instruction with JSONPath in 'find'

        Returns:
            Extracted value(s) or None
        """
        # Parse source to get JSON data
        data = self._parse_json(source)
        if data is None:
            return instruction.default

        # Execute JSONPath query
        results = self._query(data, instruction.find)

        if not results:
            return instruction.default

        # Apply filter if specified
        if instruction.filter:
            results = [r for r in results if self._matches_filter(r, instruction)]

        # Apply limit if specified
        if instruction.limit and len(results) > instruction.limit:
            results = results[: instruction.limit]

        # Return based on multiple flag
        if instruction.multiple:
            return results if results else instruction.default
        else:
            return results[0] if results else instruction.default

    def _parse_json(self, source: Any) -> Any:
        """Parse source to JSON data."""
        # Already a dict/list
        if isinstance(source, (dict, list)):
            return source

        # Try to parse as JSON string
        source_str = str(source)

        # Direct JSON parse
        try:
            return json.loads(source_str)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from HTML (e.g., script tags)
        json_patterns = [
            r"<script[^>]*type=[\"']application/json[\"'][^>]*>(.*?)</script>",
            r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
            r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});",
            r"window\.__DATA__\s*=\s*(\{.*?\});",
        ]

        for pattern in json_patterns:
            match = re.search(pattern, source_str, re.DOTALL | re.IGNORECASE)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        return None

    def _query(self, data: Any, path: str) -> list[Any]:
        """
        Execute JSONPath query.

        Args:
            data: JSON data (dict or list)
            path: JSONPath expression

        Returns:
            List of matching values
        """
        # Remove leading $
        if path.startswith("$"):
            path = path[1:]

        # Handle empty path (return root)
        if not path or path == ".":
            return [data]

        # Handle recursive descent
        if path.startswith(".."):
            field = path[2:].split(".")[0].split("[")[0]
            return self._recursive_find(data, field)

        # Remove leading dot
        if path.startswith("."):
            path = path[1:]

        return self._navigate(data, path)

    def _navigate(self, data: Any, path: str) -> list[Any]:
        """Navigate through data following path."""
        if not path:
            return [data] if data is not None else []

        # Parse next segment
        segment, remaining = self._parse_segment(path)

        if segment is None:
            return []

        # Handle array access
        if "[" in segment:
            field, index_expr = segment.split("[", 1)
            index_expr = index_expr.rstrip("]")

            # Get the field first (if any)
            if field:
                if isinstance(data, dict) and field in data:
                    data = data[field]
                else:
                    return []

            # Now handle the index
            if not isinstance(data, list):
                return []

            if index_expr == "*":
                # All elements
                results = []
                for item in data:
                    results.extend(self._navigate(item, remaining))
                return results
            else:
                # Specific index
                try:
                    idx = int(index_expr)
                    if 0 <= idx < len(data):
                        return self._navigate(data[idx], remaining)
                except ValueError:
                    pass
                return []

        # Handle field access
        if isinstance(data, dict):
            if segment in data:
                return self._navigate(data[segment], remaining)
            return []

        # Handle list - apply to all elements
        if isinstance(data, list):
            results = []
            for item in data:
                results.extend(self._navigate(item, path))
            return results

        return []

    def _parse_segment(self, path: str) -> tuple[str | None, str]:
        """Parse the next segment from a path."""
        if not path:
            return None, ""

        # Find the end of current segment
        bracket_depth = 0
        end = 0

        for i, char in enumerate(path):
            if char == "[":
                bracket_depth += 1
            elif char == "]":
                bracket_depth -= 1
            elif char == "." and bracket_depth == 0 and i > 0:
                end = i
                break
        else:
            end = len(path)

        segment = path[:end]
        remaining = path[end + 1 :] if end < len(path) else ""

        return segment, remaining

    def _recursive_find(self, data: Any, field: str) -> list[Any]:
        """Recursively find all values for a field."""
        results = []

        if isinstance(data, dict):
            if field in data:
                results.append(data[field])
            for value in data.values():
                results.extend(self._recursive_find(value, field))

        elif isinstance(data, list):
            for item in data:
                results.extend(self._recursive_find(item, field))

        return results
