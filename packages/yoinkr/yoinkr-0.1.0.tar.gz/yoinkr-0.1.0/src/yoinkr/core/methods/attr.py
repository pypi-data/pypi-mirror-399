"""Attribute extraction method."""

from typing import TYPE_CHECKING, Any, Union

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class AttrMethod(BaseMethod):
    """
    Extract HTML element attributes directly.

    This method focuses on extracting attributes from elements,
    using a selector:attribute syntax in the 'find' field.

    Syntax:
        - "selector@attribute" - Extract attribute from element(s)
        - "img@src" - Get src from img elements
        - "a@href" - Get href from anchor elements
        - ".product@data-id" - Get data-id from .product elements

    Examples:
        Instruction("image", "img.product@src", method="attr")
        Instruction("links", "a.nav@href", method="attr", multiple=True)
        Instruction("ids", "[data-item]@data-id", method="attr", multiple=True)
    """

    @property
    def name(self) -> str:
        """Method identifier."""
        return "attr"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """
        Execute attribute extraction.

        Args:
            source: HTML source (string or BeautifulSoup)
            instruction: Extraction instruction with selector@attr in 'find'

        Returns:
            Extracted attribute value(s) or None
        """
        soup = self._ensure_soup(source)

        # Parse the selector@attribute syntax
        selector, attr_name = self._parse_attr_selector(instruction.find)

        if not selector or not attr_name:
            # Fall back to using 'attribute' field from instruction
            selector = instruction.find
            attr_name = instruction.attribute

        if not attr_name:
            return instruction.default

        # Find elements
        try:
            elements = soup.select(selector)
        except Exception:
            return instruction.default

        if not elements:
            return instruction.default

        # Extract attributes
        results = []
        for el in elements:
            value = el.get(attr_name)
            if value is not None:
                # Handle list attributes (like class)
                if isinstance(value, list):
                    value = " ".join(value)

                # Apply filter
                if self._matches_filter(value, instruction):
                    results.append(value)

        if not results:
            return instruction.default

        # Apply limit
        if instruction.limit:
            results = results[: instruction.limit]

        # Return based on multiple flag
        if instruction.multiple:
            return results
        else:
            return results[0] if results else instruction.default

    def _parse_attr_selector(self, find: str) -> tuple[str, str | None]:
        """
        Parse selector@attribute syntax.

        Args:
            find: The find string (e.g., "img@src")

        Returns:
            Tuple of (selector, attribute_name)
        """
        if "@" not in find:
            return find, None

        # Handle multiple @ symbols (take the last one)
        parts = find.rsplit("@", 1)
        if len(parts) == 2:
            selector, attr = parts
            # Validate attribute name (alphanumeric, hyphens, underscores)
            if attr and all(c.isalnum() or c in "-_" for c in attr):
                return selector, attr

        return find, None


class MultiAttrMethod(BaseMethod):
    """
    Extract multiple attributes from elements at once.

    Returns a dictionary of attribute values for each element.

    Syntax in 'find':
        - "selector@attr1,attr2,attr3" - Extract multiple attributes

    Examples:
        Instruction("links", "a@href,title,target", method="multiattr", multiple=True)
        # Returns: [{"href": "...", "title": "...", "target": "..."}, ...]
    """

    @property
    def name(self) -> str:
        """Method identifier."""
        return "multiattr"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """
        Execute multi-attribute extraction.

        Args:
            source: HTML source
            instruction: Extraction instruction

        Returns:
            Dict or list of dicts with attribute values
        """
        soup = self._ensure_soup(source)

        # Parse selector@attr1,attr2,attr3
        selector, attrs = self._parse_multi_attr(instruction.find)

        if not attrs:
            return instruction.default

        # Find elements
        try:
            elements = soup.select(selector)
        except Exception:
            return instruction.default

        if not elements:
            return instruction.default

        results = []
        for el in elements:
            item = {}
            for attr in attrs:
                value = el.get(attr)
                if isinstance(value, list):
                    value = " ".join(value)
                item[attr] = value
            results.append(item)

        # Apply limit
        if instruction.limit:
            results = results[: instruction.limit]

        if instruction.multiple:
            return results
        else:
            return results[0] if results else instruction.default

    def _parse_multi_attr(self, find: str) -> tuple[str, list[str]]:
        """Parse selector@attr1,attr2 syntax."""
        if "@" not in find:
            return find, []

        parts = find.rsplit("@", 1)
        if len(parts) == 2:
            selector, attrs_str = parts
            attrs = [a.strip() for a in attrs_str.split(",") if a.strip()]
            return selector, attrs

        return find, []
