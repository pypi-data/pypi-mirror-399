"""Meta tag extraction method."""

from typing import TYPE_CHECKING, Any, Union

from .base import BaseMethod

if TYPE_CHECKING:
    from ..types import Instruction


class MetaMethod(BaseMethod):
    """Meta tag extraction."""

    @property
    def name(self) -> str:
        return "meta"

    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """Extract content from meta tags."""
        soup = self._ensure_soup(source)

        # Try different meta tag attributes: name, property, itemprop
        for attr in ["name", "property", "itemprop"]:
            if instruction.multiple:
                metas = soup.find_all("meta", attrs={attr: instruction.find})
                if metas:
                    results = []
                    limit = instruction.limit or len(metas)
                    for meta in metas[:limit]:
                        content = meta.get("content")
                        if content and self._matches_filter(content, instruction):
                            results.append(content)
                    if results:
                        return results
            else:
                meta = soup.find("meta", attrs={attr: instruction.find})
                if meta:
                    content = meta.get("content")
                    if content and self._matches_filter(content, instruction):
                        return content

        return instruction.default
