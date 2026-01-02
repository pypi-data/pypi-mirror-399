"""XPath extraction method."""

from typing import TYPE_CHECKING, Any, Optional, Union

from lxml import html as lxml_html
from lxml.etree import _Element

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class XPathMethod(BaseMethod):
    """XPath extraction."""

    @property
    def name(self) -> str:
        return "xpath"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """Extract data using XPath expressions."""
        tree = self._ensure_tree(source)
        results = tree.xpath(instruction.find)

        if instruction.multiple:
            values = []
            limit = instruction.limit or len(results)

            for r in results[:limit]:
                value = self._extract_value(r, instruction)
                if value is not None and self._matches_filter(value, instruction):
                    values.append(value)

            return values if values else instruction.default
        else:
            if results:
                value = self._extract_value(results[0], instruction)
                if self._matches_filter(value, instruction):
                    return value
            return instruction.default

    def _ensure_tree(self, source: Any) -> _Element:
        """Ensure source is an lxml tree."""
        if isinstance(source, _Element):
            return source
        html_str = str(source)
        return lxml_html.fromstring(html_str)

    def _extract_value(self, result: Any, instruction: "Instruction") -> Optional[str]:
        """Extract value from XPath result."""
        if isinstance(result, _Element):
            if instruction.attribute:
                return result.get(instruction.attribute)
            return result.text_content().strip() if result.text_content() else None
        # String result (from text() or @attribute)
        return str(result).strip() if result else None
