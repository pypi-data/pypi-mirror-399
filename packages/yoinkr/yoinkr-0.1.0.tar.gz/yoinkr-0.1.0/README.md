# Yoinkr 🎣

Yoink data from any website! A powerful, universal web scraping library that can extract any data from any website based on dynamic instructions. Designed to be consumed by Django projects as a reusable package.

## Features

- **Any URL** - No domain restrictions
- **Any Data** - Consumer defines extraction instructions dynamically
- **Multiple Methods** - CSS, XPath, Regex, Text, Meta, JSONPath, Attr extraction
- **Nested Extraction** - Lists with sub-items and scoped extraction
- **Batch Processing** - Multiple URLs with concurrency and delays
- **Proxy Support** - Built-in support for Smartproxy, Brightdata, Oxylabs
- **User Agent Rotation** - Weighted rotation mimicking real browser market share
- **Retry Logic** - Exponential backoff with jitter
- **Rate Limiting** - Token bucket algorithm with per-domain limiting
- **Circuit Breaker** - Prevent cascading failures
- **Security** - SSRF prevention, input sanitization
- **Validation System** - Text, Numeric, and Pattern validators
- **Statistics** - Track success rates, timing, throughput
- **Django Integration** - Optional models, admin, Celery tasks
- **Async First** - Built on Playwright for reliable JavaScript rendering

## Installation

```bash
# Core only
pip install yoinkr

# With Django support
pip install yoinkr[django]

# With Celery support
pip install yoinkr[celery]

# Everything
pip install yoinkr[all]

# Development
pip install yoinkr[dev]
```

After installation, install Playwright browsers:

```bash
playwright install chromium
```

## Quick Start

```python
from yoinkr import Scraper, Instruction

async def main():
    async with Scraper() as scraper:
        result = await scraper.extract(
            url="https://example.com",
            instructions=[
                Instruction("title", "h1"),
                Instruction("links", "a", attribute="href", multiple=True),
            ]
        )
    
    print(result.data)
    # {'title': 'Example Domain', 'links': ['https://www.iana.org/domains/example']}

# Run with asyncio
import asyncio
asyncio.run(main())
```

## Usage Patterns

### Simple Extraction

```python
from yoinkr import Scraper, Instruction

async with Scraper() as scraper:
    result = await scraper.extract(
        url="https://example.com/product",
        instructions=[
            Instruction("title", "h1"),
            Instruction("price", ".price", transform="float"),
            Instruction("description", ".description"),
        ]
    )

print(result.data)
# {'title': 'Product Name', 'price': 29.99, 'description': '...'}
```

### Multiple Extraction Methods

```python
async with Scraper() as scraper:
    result = await scraper.extract(
        url="https://news-site.com/article",
        instructions=[
            # CSS Selector
            Instruction("headline", "h1.article-title"),
            
            # XPath
            Instruction("author", "//span[@class='author']/text()", method="xpath"),
            
            # Regex
            Instruction("dates", r"\d{1,2}/\d{1,2}/\d{4}", method="regex", multiple=True),
            
            # Meta tags
            Instruction("og_image", "og:image", method="meta"),
            
            # Text search
            Instruction("contact", "contact us", method="text"),
            
            # JSONPath (from embedded JSON)
            Instruction("price", "$.product.price", method="jsonpath"),
            
            # Attribute extraction
            Instruction("images", "img@src", method="attr", multiple=True),
        ]
    )
```

### Nested Extraction (Lists)

```python
async with Scraper() as scraper:
    result = await scraper.extract(
        url="https://shop.com/products",
        instructions=[
            Instruction(
                name="products",
                find=".product-card",
                multiple=True,
                children=[
                    Instruction("name", ".product-name"),
                    Instruction("price", ".product-price", transform="float"),
                    Instruction("image", "img", attribute="src"),
                    Instruction("link", "a", attribute="href"),
                ]
            )
        ]
    )

# Result:
# {
#     'products': [
#         {'name': 'Item 1', 'price': 29.99, 'image': '...', 'link': '...'},
#         {'name': 'Item 2', 'price': 39.99, 'image': '...', 'link': '...'},
#     ]
# }
```

### Batch Scraping

```python
urls = [
    "https://site.com/page1",
    "https://site.com/page2",
    "https://site.com/page3",
]

instructions = [
    Instruction("title", "h1"),
    Instruction("content", ".main-content"),
]

async with Scraper() as scraper:
    results = await scraper.extract_many(
        urls=urls,
        instructions=instructions,
        concurrency=3,
        delay=(1.0, 2.0),  # Random delay between requests
    )

for result in results:
    print(f"{result.url}: {result.success}")
```

### With Rate Limiting

```python
from yoinkr import Scraper, RateLimiter

limiter = RateLimiter(requests_per_second=1.0, burst_size=5, per_domain=True)

async with Scraper() as scraper:
    async with limiter.acquire("https://example.com"):
        result = await scraper.extract(url, instructions)
```

### With Circuit Breaker

```python
from yoinkr import Scraper, CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

async with Scraper() as scraper:
    async with breaker.call("https://example.com"):
        result = await scraper.extract(url, instructions)
```

### With Security Validation

```python
from yoinkr import SecurityValidator, SecurityConfig

config = SecurityConfig(require_https=True, allow_private_ips=False)
validator = SecurityValidator(config)

# Validate URLs before scraping (prevents SSRF)
validated_url = validator.validate_url(user_provided_url)

async with Scraper() as scraper:
    result = await scraper.extract(validated_url, instructions)
```

### With Proxy

```python
from yoinkr import Scraper, ProxyBuilder

# Using proxy builder
proxy_url = ProxyBuilder.smartproxy(
    username="user",
    password="pass",
    country="ZA",  # South Africa
)

async with Scraper(proxy=proxy_url) as scraper:
    result = await scraper.extract(
        url="https://za-only-site.com",
        instructions=[...]
    )
```

### With Validation

```python
from yoinkr import (
    Scraper,
    Instruction,
    ValidationService,
    TextFieldValidator,
    NumericFieldValidator,
    PatternFieldValidator,
)

# Create validator
validator = ValidationService()
validator.register_validator("title", TextFieldValidator(required=True, min_length=1))
validator.register_validator("price", NumericFieldValidator(min_value=0))
validator.register_validator("email", PatternFieldValidator(pattern_name="email"))

async with Scraper() as scraper:
    result = await scraper.extract(url, instructions)
    
    # Validate and get clean data
    if validator.is_valid(result.data):
        clean_data = validator.get_valid_data(result.data)
    else:
        errors = validator.get_errors(result.data)
```

### With Statistics

```python
from yoinkr import Scraper, StatisticsCollector

collector = StatisticsCollector()
collector.start()

async with Scraper() as scraper:
    for url in urls:
        result = await scraper.extract(url, instructions)
        collector.record_result(result)

collector.end()
collector.print_summary()
```

### With Retry Logic

```python
from yoinkr import RetryConfig, with_retry

@with_retry(RetryConfig(max_retries=3, base_delay=1.0))
async def scrape_with_retry(scraper, url, instructions):
    return await scraper.extract(url, instructions)
```

### With Health Checks

```python
from yoinkr import HealthChecker

checker = HealthChecker()
report = await checker.check_all()

print(f"Status: {report.status}")
print(f"Browser: {report.checks['browser'].healthy}")
print(f"Dependencies: {report.checks['dependencies'].healthy}")
```

## Django Integration

### Installation

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'yoinkr.django',
]
```

Run migrations:

```bash
python manage.py migrate
```

### Using Models

```python
from yoinkr.django.models import ScrapeConfig

# Create config in admin or programmatically
config = ScrapeConfig.objects.create(
    name="product-scraper",
    default_url="https://shop.com/products",
    javascript_enabled=True,
)

# Execute
result = await config.execute()
```

### Management Command

```bash
# With inline instructions
python manage.py scrape https://example.com -i title h1 -i price .price css --pretty

# With saved config
python manage.py scrape https://example.com -c product-scraper

# With options
python manage.py scrape https://example.com -c my-config --no-js --timeout 60
```

### Celery Tasks

```python
from yoinkr.django.tasks import scrape_url_task, scrape_batch_task

# Single URL
result = scrape_url_task.delay(
    url="https://example.com",
    instructions=[
        {"name": "title", "find": "h1"},
        {"name": "price", "find": ".price", "transform": "float"},
    ],
)

# Batch
result = scrape_batch_task.delay(
    urls=["https://example.com/1", "https://example.com/2"],
    instructions=[...],
    concurrency=3,
)
```

## Configuration

### Environment Variables

Yoinkr can be configured via environment variables:

```bash
export SCRAPER_HEADLESS=true
export SCRAPER_TIMEOUT=30
export SCRAPER_LOG_LEVEL=INFO
export SCRAPER_MAX_CONCURRENT=5
export SCRAPER_RATE_LIMIT=1.0
```

```python
from yoinkr import ScraperConfig

config = ScraperConfig.from_env()
errors = config.validate()  # Check for issues
```

### Browser Presets

```python
from yoinkr import (
    DESKTOP_CONFIG,   # Standard desktop browser
    MOBILE_CONFIG,    # Mobile browser
    FAST_CONFIG,      # Fast mode (no images/JS)
    STEALTH_CONFIG,   # Stealth mode with rotation
)

async with Scraper(config=FAST_CONFIG) as scraper:
    ...
```

### Custom Browser Config

```python
from yoinkr import BrowserConfig

config = BrowserConfig(
    headless=True,
    viewport={"width": 1920, "height": 1080},
    locale="en-US",
    timezone="America/New_York",
    resource_blocking=True,
    blocked_resource_types=["image", "media", "font"],
)

async with Scraper(config=config) as scraper:
    ...
```

## API Reference

### Instruction

```python
Instruction(
    name: str,                    # Field name in output
    find: str,                    # Selector/pattern
    method: str = "css",          # css, xpath, regex, text, meta, jsonpath, attr, multiattr
    multiple: bool = False,       # Return list vs single
    attribute: str = None,        # Extract attribute
    default: Any = None,          # Default if not found
    required: bool = False,       # Raise error if not found
    transform: str = None,        # lowercase, uppercase, int, float, clean, bool
    children: List = None,        # Nested instructions
    scope: str = None,            # Scope selector
    filter: str = None,           # Regex filter
    limit: int = None,            # Max results
)
```

### Scraper

```python
Scraper(
    headless: bool = True,
    javascript: bool = True,
    timeout: int = 30,
    proxy: str = None,
    proxy_country: str = None,
    user_agent: str = None,
    viewport: dict = None,
    on_result: Callable = None,
    on_error: Callable = None,
)
```

### ScrapeResult

```python
ScrapeResult(
    url: str,
    success: bool,
    data: dict,
    status_code: int,
    final_url: str,
    page_title: str,
    html: str,              # If include_html=True
    screenshot: bytes,      # If include_screenshot=True
    fetch_time: float,
    extract_time: float,
    total_time: float,
    errors: list,
)
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Run tests
pytest

# With coverage
pytest --cov=universal_scraper --cov-report=html
```

## License

MIT License
