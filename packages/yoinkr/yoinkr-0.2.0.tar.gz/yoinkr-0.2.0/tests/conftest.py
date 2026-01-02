"""Pytest configuration and fixtures."""

import pytest

# Sample HTML for testing extraction methods
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta name="description" content="A test page for scraping">
    <meta property="og:title" content="OG Test Title">
    <meta property="og:image" content="https://example.com/image.jpg">
</head>
<body>
    <h1 class="main-title">Welcome to Test Page</h1>
    <p class="description">This is a test page for yoinkr.</p>

    <div class="product-list">
        <div class="product" data-id="1">
            <h2 class="product-name">Product One</h2>
            <span class="price">$29.99</span>
            <a href="/products/1" class="product-link">View</a>
            <img src="/images/product1.jpg" alt="Product 1">
        </div>
        <div class="product" data-id="2">
            <h2 class="product-name">Product Two</h2>
            <span class="price">$49.99</span>
            <a href="/products/2" class="product-link">View</a>
            <img src="/images/product2.jpg" alt="Product 2">
        </div>
        <div class="product" data-id="3">
            <h2 class="product-name">Product Three</h2>
            <span class="price">$99.99</span>
            <a href="/products/3" class="product-link">View</a>
            <img src="/images/product3.jpg" alt="Product 3">
        </div>
    </div>

    <div class="contact-info">
        <p>Contact us at: support@example.com</p>
        <p>Phone: +1-555-123-4567</p>
        <p>Date published: 2024-01-15</p>
    </div>

    <footer>
        <p>&copy; 2024 Test Company</p>
    </footer>
</body>
</html>
"""

SAMPLE_HTML_NESTED = """
<!DOCTYPE html>
<html>
<body>
    <div class="articles">
        <article class="post">
            <h2 class="title">First Article</h2>
            <span class="author">John Doe</span>
            <time datetime="2024-01-01">January 1, 2024</time>
            <p class="content">Content of the first article.</p>
            <div class="tags">
                <span class="tag">Python</span>
                <span class="tag">Scraping</span>
            </div>
        </article>
        <article class="post">
            <h2 class="title">Second Article</h2>
            <span class="author">Jane Smith</span>
            <time datetime="2024-01-15">January 15, 2024</time>
            <p class="content">Content of the second article.</p>
            <div class="tags">
                <span class="tag">Django</span>
                <span class="tag">Web</span>
            </div>
        </article>
    </div>
</body>
</html>
"""


@pytest.fixture
def sample_html() -> str:
    """Return sample HTML for testing."""
    return SAMPLE_HTML


@pytest.fixture
def sample_html_nested() -> str:
    """Return sample HTML with nested structure."""
    return SAMPLE_HTML_NESTED


@pytest.fixture
def sample_soup(sample_html: str):
    """Return BeautifulSoup object from sample HTML."""
    from bs4 import BeautifulSoup

    return BeautifulSoup(sample_html, "html.parser")
