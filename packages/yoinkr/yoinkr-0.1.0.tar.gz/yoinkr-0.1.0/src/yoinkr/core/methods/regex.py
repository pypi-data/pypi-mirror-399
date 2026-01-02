"""Regex extraction method."""

import re
from typing import TYPE_CHECKING, Any, Union

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class RegexMethod(BaseMethod):
    """Regex pattern extraction."""

    @property
    def name(self) -> str:
        return "regex"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """Extract data using regex patterns."""
        text = self._get_text(source)
        pattern = re.compile(instruction.find, re.IGNORECASE | re.DOTALL)

        if instruction.multiple:
            matches = pattern.findall(text)
            results = self._process_matches(matches, instruction)

            if instruction.limit:
                results = results[: instruction.limit]

            # Apply filter
            results = [r for r in results if self._matches_filter(r, instruction)]

            return results if results else instruction.default
        else:
            match = pattern.search(text)
            if match:
                group = instruction.regex_group if instruction.regex_group is not None else 0
                try:
                    value = match.group(group)
                    if self._matches_filter(value, instruction):
                        return value
                except IndexError:
                    return instruction.default
            return instruction.default

    def _process_matches(self, matches: list[Any], instruction: "Instruction") -> list[str]:
        """Process regex matches."""
        results = []
        group = instruction.regex_group if instruction.regex_group is not None else 0

        for match in matches:
            if isinstance(match, tuple):
                # Multiple groups - get specific group or first
                if group < len(match):
                    results.append(match[group])
                elif match:
                    results.append(match[0])
            else:
                # Single group or full match
                results.append(match)

        return results
