"""Base class for extraction methods."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Union

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from ..types import Instruction


class BaseMethod(ABC):
    """Base class for extraction methods."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Method identifier."""
        pass

    @abstractmethod
    async def extract(
        self,
        source: Any,
        instruction: "Instruction",
    ) -> Union[Any, list[Any], None]:
        """
        Execute extraction.

        Args:
            source: HTML source (string or BeautifulSoup)
            instruction: Extraction instruction

        Returns:
            Extracted value(s) or None
        """
        pass

    def _ensure_soup(self, source: Any) -> BeautifulSoup:
        """Ensure source is a BeautifulSoup object."""
        if isinstance(source, BeautifulSoup):
            return source
        return BeautifulSoup(str(source), "html.parser")

    def _get_text(self, source: Any) -> str:
        """Get text content from source."""
        if isinstance(source, BeautifulSoup):
            return source.get_text()
        if hasattr(source, "get_text"):
            return source.get_text()
        return str(source)

    def _matches_filter(self, value: Any, instruction: "Instruction") -> bool:
        """Check if value matches the filter pattern."""
        import re

        if not instruction.filter:
            return True
        if value is None:
            return False
        return bool(re.search(instruction.filter, str(value)))
