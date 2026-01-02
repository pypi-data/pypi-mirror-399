"""Extraction pipeline for the universal scraper."""

import re
from typing import Any, Callable, Optional

from bs4 import BeautifulSoup

from .methods import (
    AttrMethod,
    BaseMethod,
    CSSMethod,
    JSONPathMethod,
    MetaMethod,
    MultiAttrMethod,
    RegexMethod,
    TextMethod,
    XPathMethod,
)
from .types import Instruction, Method


class MethodRegistry:
    """Registry of extraction methods."""

    def __init__(self) -> None:
        self._methods: dict[str, BaseMethod] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register default extraction methods."""
        for method in [
            CSSMethod(),
            XPathMethod(),
            RegexMethod(),
            MetaMethod(),
            TextMethod(),
            JSONPathMethod(),
            AttrMethod(),
            MultiAttrMethod(),
        ]:
            self._methods[method.name] = method

    def register(self, method: BaseMethod) -> None:
        """Register a custom extraction method."""
        self._methods[method.name] = method

    def get(self, name: str) -> BaseMethod:
        """Get a method by name."""
        if name not in self._methods:
            raise ValueError(f"Unknown method: {name}. Available: {list(self._methods.keys())}")
        return self._methods[name]

    def available_methods(self) -> list[str]:
        """Get list of available method names."""
        return list(self._methods.keys())


class Extractor:
    """Extraction pipeline."""

    def __init__(self, registry: Optional[MethodRegistry] = None) -> None:
        self.registry = registry or MethodRegistry()
        self._transforms: dict[str, Callable[[Any], Any]] = {
            "lowercase": lambda x: x.lower() if isinstance(x, str) else x,
            "uppercase": lambda x: x.upper() if isinstance(x, str) else x,
            "strip": lambda x: x.strip() if isinstance(x, str) else x,
            "int": self._to_int,
            "float": self._to_float,
            "clean": lambda x: " ".join(str(x).split()) if x else None,
            "bool": self._to_bool,
        }

    async def extract(
        self,
        source: Any,
        instructions: list[Instruction],
    ) -> dict[str, Any]:
        """
        Run all instructions and return results.

        Args:
            source: HTML source (string or BeautifulSoup)
            instructions: List of extraction instructions

        Returns:
            Dict with 'data' and 'errors' keys
        """
        results: dict[str, Any] = {}
        errors: list[dict[str, str]] = []

        for instr in instructions:
            try:
                # Get method
                method_name = (
                    instr.method.value if isinstance(instr.method, Method) else instr.method
                )
                method = self.registry.get(method_name)

                # Handle scoped extraction
                if instr.scope:
                    value = await self._extract_scoped(source, instr, method)
                else:
                    value = await method.extract(source, instr)

                # Apply transform
                if instr.transform and value is not None:
                    value = self._apply_transform(value, instr.transform)

                # Handle nested/children
                if instr.children and value is not None:
                    value = await self._extract_nested(source, instr)

                results[instr.name] = value

                # Check required
                if instr.required and value is None:
                    errors.append({"field": instr.name, "error": "Required field not found"})

            except Exception as e:
                errors.append({"field": instr.name, "error": str(e)})
                results[instr.name] = instr.default

        return {"data": results, "errors": errors}

    async def _extract_scoped(self, source: Any, instr: Instruction, method: BaseMethod) -> Any:
        """Extract within a scoped element."""
        soup = BeautifulSoup(source, "html.parser") if isinstance(source, str) else source

        scope_elements = soup.select(instr.scope) if instr.scope else []
        if not scope_elements:
            return instr.default

        if instr.multiple:
            results = []
            limit = instr.limit or len(scope_elements)
            for scope_el in scope_elements[:limit]:
                val = await method.extract(str(scope_el), instr)
                if val is not None:
                    if isinstance(val, list):
                        results.extend(val)
                    else:
                        results.append(val)
            return results or instr.default
        else:
            return await method.extract(str(scope_elements[0]), instr)

    async def _extract_nested(self, source: Any, parent_instr: Instruction) -> Any:
        """Extract children within parent elements."""
        soup = BeautifulSoup(source, "html.parser") if isinstance(source, str) else source

        # Find parent elements
        containers = soup.select(parent_instr.find)
        if not containers:
            return parent_instr.default

        results = []
        limit = parent_instr.limit or len(containers)

        for container in containers[:limit]:
            item: dict[str, Any] = {}

            for child in parent_instr.children or []:
                method_name = (
                    child.method.value if isinstance(child.method, Method) else child.method
                )
                method = self.registry.get(method_name)
                item[child.name] = await method.extract(str(container), child)

                if child.transform and item[child.name] is not None:
                    item[child.name] = self._apply_transform(item[child.name], child.transform)

            results.append(item)

        return results if results else parent_instr.default

    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply a transform to a value."""
        if transform not in self._transforms:
            return value

        if isinstance(value, list):
            return [self._transforms[transform](v) for v in value]
        return self._transforms[transform](value)

    def register_transform(self, name: str, func: Callable[[Any], Any]) -> None:
        """Register a custom transform function."""
        self._transforms[name] = func

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        """Convert value to integer."""
        if value is None:
            return None
        cleaned = re.sub(r"[^\d\-]", "", str(value))
        return int(cleaned) if cleaned and cleaned != "-" else None

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        """Convert value to float."""
        if value is None:
            return None
        cleaned = re.sub(r"[^\d.\-]", "", str(value))
        try:
            return float(cleaned) if cleaned and cleaned != "-" else None
        except ValueError:
            return None

    @staticmethod
    def _to_bool(value: Any) -> Optional[bool]:
        """Convert value to boolean."""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        str_val = str(value).lower().strip()
        if str_val in ("true", "1", "yes", "on"):
            return True
        if str_val in ("false", "0", "no", "off"):
            return False
        return None
