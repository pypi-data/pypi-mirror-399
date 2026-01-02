"""Text search extraction method."""

from typing import TYPE_CHECKING, Any, Union

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class TextMethod(BaseMethod):
    """Simple text search extraction."""

    @property
    def name(self) -> str:
        return "text"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """Extract lines containing the search text."""
        text = self._get_text(source)
        search = instruction.find.lower()

        # Find lines containing the search text
        lines = [
            line.strip() for line in text.split("\n") if search in line.lower() and line.strip()
        ]

        # Apply filter
        lines = [line for line in lines if self._matches_filter(line, instruction)]

        if instruction.multiple:
            if instruction.limit:
                lines = lines[: instruction.limit]
            return lines if lines else instruction.default
        else:
            return lines[0] if lines else instruction.default
