"""
Security validation and input sanitization for web scraping.

This module provides URL validation, input sanitization, and security
checks to prevent common vulnerabilities.

Example:
    >>> validator = SecurityValidator()
    >>> validator.validate_url("https://example.com")  # OK
    >>> validator.validate_url("file:///etc/passwd")  # Raises SecurityError
"""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass, field
from typing import Pattern
from urllib.parse import urlparse

from ..utils.logging import get_logger
from .exceptions import SecurityError

logger = get_logger(__name__)


@dataclass
class SecurityConfig:
    """
    Security configuration for the scraper.

    Attributes:
        allowed_schemes: URL schemes that are allowed (e.g., https, http)
        blocked_hosts: Hostnames that are blocked
        blocked_ip_ranges: IP ranges that are blocked (CIDR notation)
        allow_private_ips: Whether to allow private IP addresses
        allow_localhost: Whether to allow localhost
        max_url_length: Maximum URL length
        max_redirects: Maximum number of redirects to follow
        blocked_patterns: Regex patterns for blocked URLs
        require_https: Whether to require HTTPS
    """

    allowed_schemes: set[str] = field(default_factory=lambda: {"http", "https"})
    blocked_hosts: set[str] = field(default_factory=set)
    blocked_ip_ranges: list[str] = field(default_factory=list)
    allow_private_ips: bool = False
    allow_localhost: bool = False
    max_url_length: int = 2048
    max_redirects: int = 10
    blocked_patterns: list[str] = field(default_factory=list)
    require_https: bool = False

    def __post_init__(self) -> None:
        """Compile blocked patterns."""
        self._compiled_patterns: list[Pattern[str]] = []
        for pattern in self.blocked_patterns:
            try:
                self._compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                logger.warning(f"Invalid blocked pattern '{pattern}': {e}")

        # Parse IP ranges
        self._parsed_ip_ranges: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for range_str in self.blocked_ip_ranges:
            try:
                self._parsed_ip_ranges.append(ipaddress.ip_network(range_str, strict=False))
            except ValueError as e:
                logger.warning(f"Invalid IP range '{range_str}': {e}")


class SecurityValidator:
    """
    Validates URLs and inputs for security.

    This validator helps prevent:
    - SSRF (Server-Side Request Forgery)
    - Access to private networks
    - Malicious URL patterns
    - Excessively long URLs

    Example:
        >>> config = SecurityConfig(require_https=True)
        >>> validator = SecurityValidator(config)
        >>> validator.validate_url("http://example.com")
        Raises SecurityError: HTTPS required
    """

    # Private IP ranges
    PRIVATE_IP_RANGES = [
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local
        ipaddress.ip_network("::1/128"),  # IPv6 loopback
        ipaddress.ip_network("fc00::/7"),  # IPv6 private
        ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ]

    # Cloud metadata endpoints (SSRF targets)
    METADATA_HOSTS = {
        "169.254.169.254",  # AWS, GCP, Azure
        "metadata.google.internal",
        "metadata.goog",
        "169.254.170.2",  # ECS task metadata
    }

    def __init__(self, config: SecurityConfig | None = None) -> None:
        self.config = config or SecurityConfig()

    def validate_url(self, url: str) -> str:
        """
        Validate a URL for security.

        Args:
            url: The URL to validate

        Returns:
            The validated URL (may be normalized)

        Raises:
            SecurityError: If the URL fails validation
        """
        # Check URL length
        if len(url) > self.config.max_url_length:
            raise SecurityError(
                f"URL exceeds maximum length of {self.config.max_url_length} characters"
            )

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise SecurityError(f"Invalid URL format: {e}")

        # Check scheme
        if not parsed.scheme:
            raise SecurityError("URL must have a scheme (http or https)")

        if parsed.scheme.lower() not in self.config.allowed_schemes:
            raise SecurityError(
                f"URL scheme '{parsed.scheme}' not allowed. Allowed: {self.config.allowed_schemes}"
            )

        # Check HTTPS requirement
        if self.config.require_https and parsed.scheme.lower() != "https":
            raise SecurityError("HTTPS is required")

        # Check for host
        if not parsed.netloc:
            raise SecurityError("URL must have a host")

        # Extract hostname (handle IPv6)
        hostname = parsed.hostname
        if not hostname:
            raise SecurityError("Could not extract hostname from URL")

        # Check blocked hosts
        if hostname.lower() in self.config.blocked_hosts:
            raise SecurityError(f"Host '{hostname}' is blocked")

        # Check metadata endpoints (SSRF prevention)
        if hostname.lower() in self.METADATA_HOSTS:
            raise SecurityError(
                f"Access to metadata endpoint '{hostname}' is blocked (SSRF prevention)"
            )

        # Check blocked patterns
        for pattern in self.config._compiled_patterns:
            if pattern.search(url):
                raise SecurityError(f"URL matches blocked pattern: {pattern.pattern}")

        # Resolve and check IP
        self._validate_host_ip(hostname)

        logger.debug(f"URL validated: {url}")
        return url

    def _validate_host_ip(self, hostname: str) -> None:
        """Validate the IP address of a hostname."""
        try:
            # Check if hostname is already an IP
            ip = ipaddress.ip_address(hostname)
            self._check_ip_address(ip, hostname)
        except ValueError:
            # Hostname is not an IP, resolve it
            try:
                # Get all IPs for the hostname
                addr_info = socket.getaddrinfo(hostname, None)
                for info in addr_info:
                    ip_str = info[4][0]
                    try:
                        ip = ipaddress.ip_address(ip_str)
                        self._check_ip_address(ip, hostname)
                    except ValueError:
                        continue
            except socket.gaierror:
                # DNS resolution failed - this is OK, might work with different resolver
                logger.debug(f"Could not resolve hostname: {hostname}")

    def _check_ip_address(
        self, ip: ipaddress.IPv4Address | ipaddress.IPv6Address, hostname: str
    ) -> None:
        """Check if an IP address is allowed."""
        # Check localhost
        if ip.is_loopback and not self.config.allow_localhost:
            raise SecurityError(f"Localhost access is blocked for '{hostname}'")

        # Check private IPs
        if ip.is_private and not self.config.allow_private_ips:
            raise SecurityError(f"Private IP access is blocked for '{hostname}' ({ip})")

        # Check blocked IP ranges from config
        for ip_range in self.config._parsed_ip_ranges:
            if ip in ip_range:
                raise SecurityError(f"IP {ip} is in blocked range {ip_range}")

    def sanitize_selector(self, selector: str) -> str:
        """
        Sanitize a CSS/XPath selector.

        Args:
            selector: The selector to sanitize

        Returns:
            The sanitized selector

        Raises:
            SecurityError: If the selector contains dangerous patterns
        """
        # Check for common injection patterns
        dangerous_patterns = [
            r"javascript:",
            r"data:",
            r"vbscript:",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
        ]

        selector_lower = selector.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, selector_lower, re.IGNORECASE):
                raise SecurityError(f"Selector contains dangerous pattern: {pattern}")

        return selector

    def sanitize_regex(self, pattern: str) -> str:
        """
        Sanitize a regex pattern.

        Args:
            pattern: The regex pattern to sanitize

        Returns:
            The sanitized pattern

        Raises:
            SecurityError: If the pattern is dangerous (ReDoS risk)
        """
        # Check for catastrophic backtracking patterns
        redos_patterns = [
            r"\(\.\*\)\+",  # (.*)+
            r"\(\.\+\)\+",  # (.+)+
            r"\([^)]*\)\*\1",  # Nested quantifiers with backreference
            r"\(\[.*?\]\+\)\+",  # ([...]+)+
        ]

        for redos in redos_patterns:
            if re.search(redos, pattern):
                raise SecurityError(f"Regex pattern may cause ReDoS: {pattern}")

        # Try to compile the pattern to check validity
        try:
            re.compile(pattern)
        except re.error as e:
            raise SecurityError(f"Invalid regex pattern: {e}")

        return pattern

    def validate_instruction(self, instruction: dict) -> dict:
        """
        Validate a scraping instruction for security.

        Args:
            instruction: The instruction dictionary to validate

        Returns:
            The validated instruction

        Raises:
            SecurityError: If the instruction contains dangerous content
        """
        validated = {}

        for key, value in instruction.items():
            if key == "selector" and isinstance(value, str):
                validated[key] = self.sanitize_selector(value)
            elif key == "pattern" and isinstance(value, str):
                validated[key] = self.sanitize_regex(value)
            elif isinstance(value, dict):
                validated[key] = self.validate_instruction(value)
            elif isinstance(value, list):
                validated[key] = [
                    self.validate_instruction(v) if isinstance(v, dict) else v for v in value
                ]
            else:
                validated[key] = value

        return validated


def sanitize_output(data: str, max_length: int = 1_000_000) -> str:
    """
    Sanitize scraped output data.

    Args:
        data: The data to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized data

    Raises:
        SecurityError: If data exceeds max length
    """
    if len(data) > max_length:
        raise SecurityError(f"Output data exceeds maximum length of {max_length}")

    # Remove null bytes
    data = data.replace("\x00", "")

    return data


def validate_proxy_url(url: str) -> str:
    """
    Validate a proxy URL.

    Args:
        url: The proxy URL to validate

    Returns:
        The validated proxy URL

    Raises:
        SecurityError: If the proxy URL is invalid
    """
    parsed = urlparse(url)

    allowed_schemes = {"http", "https", "socks4", "socks5"}
    if parsed.scheme.lower() not in allowed_schemes:
        raise SecurityError(
            f"Proxy scheme '{parsed.scheme}' not allowed. Allowed: {allowed_schemes}"
        )

    if not parsed.hostname:
        raise SecurityError("Proxy URL must have a hostname")

    if not parsed.port:
        raise SecurityError("Proxy URL must have a port")

    return url
