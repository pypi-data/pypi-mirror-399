"""User agent rotation utilities."""

import random
from typing import Optional

# User agent distribution based on real browser market share
USER_AGENT_DISTRIBUTION: dict[str, list[tuple[str, float]]] = {
    "chrome": [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            0.35,
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            0.20,
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            0.10,
        ),
    ],
    "firefox": [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            0.10,
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            0.05,
        ),
    ],
    "safari": [
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            0.10,
        ),
    ],
    "edge": [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            0.08,
        ),
    ],
    "mobile": [
        (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            0.02,
        ),
    ],
}


class UserAgentSelector:
    """Weighted user agent rotation."""

    def __init__(
        self,
        distribution: Optional[dict[str, list[tuple[str, float]]]] = None,
        include_mobile: bool = False,
    ) -> None:
        """
        Initialize the selector.

        Args:
            distribution: Custom user agent distribution
            include_mobile: Whether to include mobile user agents
        """
        self.distribution = distribution or USER_AGENT_DISTRIBUTION
        self.include_mobile = include_mobile
        self._build_weighted_list()

    def _build_weighted_list(self) -> None:
        """Build weighted list for random selection."""
        self.agents: list[str] = []
        self.weights: list[float] = []

        for category, agents in self.distribution.items():
            if category == "mobile" and not self.include_mobile:
                continue

            for agent, weight in agents:
                self.agents.append(agent)
                self.weights.append(weight)

        # Normalize weights
        total = sum(self.weights)
        if total > 0:
            self.weights = [w / total for w in self.weights]

    def get_random(self) -> str:
        """
        Get a random user agent based on weights.

        Returns:
            Random user agent string
        """
        if not self.agents:
            return self.get_chrome()
        return random.choices(self.agents, weights=self.weights, k=1)[0]

    def get_for_browser(self, browser: str) -> Optional[str]:
        """
        Get random user agent for specific browser.

        Args:
            browser: Browser name (chrome, firefox, safari, edge, mobile)

        Returns:
            Random user agent for the browser, or None if not found
        """
        if browser in self.distribution:
            agents = self.distribution[browser]
            return random.choice([a for a, _ in agents])
        return None

    @classmethod
    def get_chrome(cls) -> str:
        """Get a Chrome user agent."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    @classmethod
    def get_firefox(cls) -> str:
        """Get a Firefox user agent."""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"

    @classmethod
    def get_safari(cls) -> str:
        """Get a Safari user agent."""
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        )

    @classmethod
    def get_mobile(cls) -> str:
        """Get a mobile user agent."""
        return (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        )
