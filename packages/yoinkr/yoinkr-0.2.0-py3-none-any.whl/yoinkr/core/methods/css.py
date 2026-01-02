"""CSS selector extraction method."""

from typing import TYPE_CHECKING, Any, Optional, Union

from bs4 import Tag

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class CSSMethod(BaseMethod):
    """CSS Selector extraction."""

    @property
    def name(self) -> str:
        return "css"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """Extract data using CSS selectors."""
        soup = self._ensure_soup(source)

        if instruction.multiple:
            elements = soup.select(instruction.find)
            results = []

            limit = instruction.limit or len(elements)
            for el in elements[:limit]:
                value = self._get_value(el, instruction)
                if value is not None and self._matches_filter(value, instruction):
                    results.append(value)

            return results if results else instruction.default
        else:
            element = soup.select_one(instruction.find)
            if element:
                value = self._get_value(element, instruction)
                if self._matches_filter(value, instruction):
                    return value
            return instruction.default

    def _get_value(self, element: Tag, instruction: "Instruction") -> Optional[str]:
        """Get value from element based on instruction."""
        if instruction.attribute:
            value = element.get(instruction.attribute)
            # Handle list attributes (like class)
            if isinstance(value, list):
                return " ".join(value)
            return value
        return element.get_text(strip=True)
