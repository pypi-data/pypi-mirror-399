"""
Extraction methods for yoinkr.

This module provides various extraction strategies for pulling data from web pages:

- **CSSMethod**: Extract using CSS selectors (BeautifulSoup)
- **XPathMethod**: Extract using XPath expressions (lxml)
- **RegexMethod**: Extract using regular expressions
- **TextMethod**: Search for text patterns
- **MetaMethod**: Extract meta tag content
- **JSONPathMethod**: Extract from JSON data using JSONPath
- **AttrMethod**: Extract HTML element attributes
- **MultiAttrMethod**: Extract multiple attributes at once

All methods inherit from BaseMethod and can be registered with MethodRegistry.

Example:
    >>> from yoinkr.core.methods import CSSMethod, MethodRegistry
    >>> registry = MethodRegistry()
    >>> registry.register(CSSMethod())
    >>> method = registry.get("css")
"""

from .attr import AttrMethod, MultiAttrMethod
from .base import BaseMethod
from .css import CSSMethod
from .jsonpath import JSONPathMethod
from .meta import MetaMethod
from .regex import RegexMethod
from .text import TextMethod
from .xpath import XPathMethod

__all__ = [
    "BaseMethod",
    "CSSMethod",
    "XPathMethod",
    "RegexMethod",
    "TextMethod",
    "MetaMethod",
    "JSONPathMethod",
    "AttrMethod",
    "MultiAttrMethod",
]
