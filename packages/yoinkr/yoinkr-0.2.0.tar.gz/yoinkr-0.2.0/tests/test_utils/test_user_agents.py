"""Tests for user agent utilities."""

import pytest

from yoinkr.utils.user_agents import (
    USER_AGENT_DISTRIBUTION,
    UserAgentSelector,
)


class TestUserAgentSelector:
    """Tests for UserAgentSelector."""

    def test_get_random(self):
        """Test getting random user agent."""
        selector = UserAgentSelector()
        ua = selector.get_random()

        assert ua is not None
        assert "Mozilla" in ua

    def test_get_random_consistency(self):
        """Test that random selection is consistent."""
        selector = UserAgentSelector()

        # Get multiple random agents
        agents = [selector.get_random() for _ in range(10)]

        # All should be valid user agents
        for ua in agents:
            assert "Mozilla" in ua

    def test_get_for_browser_chrome(self):
        """Test getting Chrome user agent."""
        selector = UserAgentSelector()
        ua = selector.get_for_browser("chrome")

        assert ua is not None
        assert "Chrome" in ua

    def test_get_for_browser_firefox(self):
        """Test getting Firefox user agent."""
        selector = UserAgentSelector()
        ua = selector.get_for_browser("firefox")

        assert ua is not None
        assert "Firefox" in ua

    def test_get_for_browser_unknown(self):
        """Test getting unknown browser returns None."""
        selector = UserAgentSelector()
        ua = selector.get_for_browser("unknown")

        assert ua is None

    def test_include_mobile(self):
        """Test including mobile user agents."""
        selector_no_mobile = UserAgentSelector(include_mobile=False)
        selector_with_mobile = UserAgentSelector(include_mobile=True)

        # With mobile should have more agents
        assert len(selector_with_mobile.agents) >= len(selector_no_mobile.agents)

    def test_get_chrome_class_method(self):
        """Test class method for Chrome UA."""
        ua = UserAgentSelector.get_chrome()
        assert "Chrome" in ua

    def test_get_firefox_class_method(self):
        """Test class method for Firefox UA."""
        ua = UserAgentSelector.get_firefox()
        assert "Firefox" in ua

    def test_get_safari_class_method(self):
        """Test class method for Safari UA."""
        ua = UserAgentSelector.get_safari()
        assert "Safari" in ua

    def test_get_mobile_class_method(self):
        """Test class method for mobile UA."""
        ua = UserAgentSelector.get_mobile()
        assert "Mobile" in ua
        assert "iPhone" in ua

    def test_custom_distribution(self):
        """Test custom user agent distribution."""
        custom = {
            "custom": [("Custom Agent 1.0", 1.0)],
        }
        selector = UserAgentSelector(distribution=custom)

        ua = selector.get_random()
        assert ua == "Custom Agent 1.0"


class TestUserAgentDistribution:
    """Tests for user agent distribution."""

    def test_distribution_has_chrome(self):
        """Test distribution includes Chrome."""
        assert "chrome" in USER_AGENT_DISTRIBUTION

    def test_distribution_has_firefox(self):
        """Test distribution includes Firefox."""
        assert "firefox" in USER_AGENT_DISTRIBUTION

    def test_distribution_weights_sum(self):
        """Test that weights are reasonable."""
        total = 0
        for category, agents in USER_AGENT_DISTRIBUTION.items():
            for _, weight in agents:
                total += weight

        # Total should be approximately 1.0 (allowing for rounding)
        assert 0.9 <= total <= 1.1
