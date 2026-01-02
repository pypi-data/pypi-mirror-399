"""Proxy URL builder for various providers."""

from typing import Optional
from urllib.parse import quote


class ProxyBuilder:
    """Build proxy URLs for various providers."""

    @staticmethod
    def build_url(
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        protocol: str = "http",
    ) -> str:
        """
        Build a basic proxy URL.

        Args:
            host: Proxy host
            port: Proxy port
            username: Optional username
            password: Optional password
            protocol: Protocol (http or https)

        Returns:
            Formatted proxy URL
        """
        if username and password:
            return f"{protocol}://{quote(username)}:{quote(password)}@{host}:{port}"
        return f"{protocol}://{host}:{port}"

    @staticmethod
    def smartproxy(
        username: str,
        password: str,
        country: Optional[str] = None,
        city: Optional[str] = None,
        session_type: str = "rotating",  # 'rotating' or 'sticky'
        session_id: Optional[str] = None,
        host: str = "gate.smartproxy.com",
        port: int = 10001,
    ) -> str:
        """
        Build Smartproxy URL.

        Args:
            username: Smartproxy username
            password: Smartproxy password
            country: ISO country code (e.g., 'ZA', 'US')
            city: City name
            session_type: 'rotating' or 'sticky'
            session_id: Session ID for sticky sessions
            host: Proxy host
            port: Proxy port

        Returns:
            Formatted Smartproxy URL
        """
        user_parts = [username]

        if country:
            user_parts.append(f"country-{country.lower()}")

        if city:
            user_parts.append(f"city-{city.lower()}")

        if session_type == "sticky" and session_id:
            user_parts.append(f"session-{session_id}")

        full_username = "-".join(user_parts)
        return f"http://{quote(full_username)}:{quote(password)}@{host}:{port}"

    @staticmethod
    def brightdata(
        username: str,
        password: str,
        zone: str,
        country: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Build Bright Data (Luminati) proxy URL.

        Args:
            username: Bright Data customer username
            password: Bright Data password
            zone: Zone name
            country: ISO country code
            session_id: Session ID for sticky sessions

        Returns:
            Formatted Bright Data proxy URL
        """
        user_parts = [f"lum-customer-{username}", f"zone-{zone}"]

        if country:
            user_parts.append(f"country-{country.lower()}")

        if session_id:
            user_parts.append(f"session-{session_id}")

        full_username = "-".join(user_parts)
        return f"http://{full_username}:{password}@brd.superproxy.io:22225"

    @staticmethod
    def oxylabs(
        username: str,
        password: str,
        country: Optional[str] = None,
        city: Optional[str] = None,
        session_type: str = "rotating",
    ) -> str:
        """
        Build Oxylabs proxy URL.

        Args:
            username: Oxylabs customer username
            password: Oxylabs password
            country: ISO country code
            city: City name
            session_type: 'rotating' or 'sticky'

        Returns:
            Formatted Oxylabs proxy URL
        """
        import random

        user_parts = [f"customer-{username}"]

        if country:
            user_parts.append(f"cc-{country.lower()}")

        if city:
            user_parts.append(f"city-{city.lower()}")

        if session_type == "sticky":
            session = random.randint(1000000, 9999999)
            user_parts.append(f"sessid-{session}")

        full_username = "-".join(user_parts)
        return f"http://{full_username}:{password}@pr.oxylabs.io:7777"

    @staticmethod
    def datacenter(
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> str:
        """
        Build a datacenter proxy URL.

        Args:
            host: Proxy host
            port: Proxy port
            username: Optional username
            password: Optional password

        Returns:
            Formatted proxy URL
        """
        return ProxyBuilder.build_url(host, port, username, password)


def south_africa_proxy(username: str, password: str, provider: str = "smartproxy") -> str:
    """
    Get a South African proxy URL.

    Args:
        username: Provider username
        password: Provider password
        provider: Provider name (smartproxy, brightdata, oxylabs)

    Returns:
        Formatted proxy URL for South Africa
    """
    if provider == "smartproxy":
        return ProxyBuilder.smartproxy(username, password, country="ZA")
    elif provider == "brightdata":
        return ProxyBuilder.brightdata(username, password, zone="residential", country="ZA")
    elif provider == "oxylabs":
        return ProxyBuilder.oxylabs(username, password, country="ZA")
    raise ValueError(f"Unknown provider: {provider}")
