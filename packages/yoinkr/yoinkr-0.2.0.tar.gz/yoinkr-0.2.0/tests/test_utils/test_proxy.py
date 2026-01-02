"""Tests for proxy utilities."""

import pytest

from yoinkr.utils.proxy import ProxyBuilder, south_africa_proxy


class TestProxyBuilder:
    """Tests for ProxyBuilder."""

    def test_build_url_basic(self):
        """Test building basic proxy URL."""
        url = ProxyBuilder.build_url("proxy.example.com", 8080)
        assert url == "http://proxy.example.com:8080"

    def test_build_url_with_auth(self):
        """Test building proxy URL with authentication."""
        url = ProxyBuilder.build_url("proxy.example.com", 8080, "user", "pass123")
        assert url == "http://user:pass123@proxy.example.com:8080"

    def test_build_url_with_https(self):
        """Test building HTTPS proxy URL."""
        url = ProxyBuilder.build_url("proxy.example.com", 8080, protocol="https")
        assert url == "https://proxy.example.com:8080"

    def test_build_url_escapes_special_chars(self):
        """Test that special characters are URL encoded."""
        url = ProxyBuilder.build_url("proxy.example.com", 8080, "user@domain", "p@ss:word")
        assert "user%40domain" in url
        assert "p%40ss%3Aword" in url

    def test_smartproxy_basic(self):
        """Test Smartproxy URL building."""
        url = ProxyBuilder.smartproxy("user", "pass")
        assert "gate.smartproxy.com" in url
        assert "user:pass" in url

    def test_smartproxy_with_country(self):
        """Test Smartproxy URL with country."""
        url = ProxyBuilder.smartproxy("user", "pass", country="ZA")
        assert "country-za" in url

    def test_smartproxy_with_city(self):
        """Test Smartproxy URL with city."""
        url = ProxyBuilder.smartproxy("user", "pass", country="US", city="new_york")
        assert "country-us" in url
        assert "city-new_york" in url

    def test_smartproxy_sticky_session(self):
        """Test Smartproxy sticky session."""
        url = ProxyBuilder.smartproxy("user", "pass", session_type="sticky", session_id="abc123")
        assert "session-abc123" in url

    def test_brightdata_basic(self):
        """Test Bright Data URL building."""
        url = ProxyBuilder.brightdata("customer", "pass", zone="residential")
        assert "brd.superproxy.io" in url
        assert "lum-customer-customer" in url
        assert "zone-residential" in url

    def test_brightdata_with_country(self):
        """Test Bright Data URL with country."""
        url = ProxyBuilder.brightdata("customer", "pass", zone="residential", country="ZA")
        assert "country-za" in url

    def test_oxylabs_basic(self):
        """Test Oxylabs URL building."""
        url = ProxyBuilder.oxylabs("customer", "pass")
        assert "pr.oxylabs.io" in url
        assert "customer-customer" in url

    def test_oxylabs_with_country(self):
        """Test Oxylabs URL with country."""
        url = ProxyBuilder.oxylabs("customer", "pass", country="ZA")
        assert "cc-za" in url


class TestSouthAfricaProxy:
    """Tests for south_africa_proxy helper."""

    def test_smartproxy(self):
        """Test South Africa proxy with Smartproxy."""
        url = south_africa_proxy("user", "pass", provider="smartproxy")
        assert "country-za" in url
        assert "gate.smartproxy.com" in url

    def test_brightdata(self):
        """Test South Africa proxy with Bright Data."""
        url = south_africa_proxy("user", "pass", provider="brightdata")
        assert "country-za" in url
        assert "brd.superproxy.io" in url

    def test_oxylabs(self):
        """Test South Africa proxy with Oxylabs."""
        url = south_africa_proxy("user", "pass", provider="oxylabs")
        assert "cc-za" in url
        assert "pr.oxylabs.io" in url

    def test_unknown_provider_raises(self):
        """Test that unknown provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider"):
            south_africa_proxy("user", "pass", provider="unknown")
