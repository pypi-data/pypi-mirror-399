# Scrapy_ZenRows Middleware

This is a Scrapy middlware that provides an interface for interacting with the ZenRows® Scraper API in your Scrapy spiders. It lets you enjoy all the features of the ZenRows® Scraper API while using scrapy.

## Introduction

The ZenRows® Scraper API is an all-in-one toolkit designed to simplify and enhance the process of extracting data from websites. Whether you're dealing with static or dynamic content, our API provides a range of features to meet your scraping needs efficiently.

With Premium Proxies, ZenRows gives you access to over 55 million residential IPs from 190+ countries, ensuring 99.9% uptime and highly reliable scraping sessions. Our system also handles advanced fingerprinting, header rotation, and IP management, **enabling you to scrape even the most protected sites without needing to manually configure these elements**.

ZenRows makes it easy to bypass complex anti-bot measures, handle JavaScript-heavy sites, and interact with web elements dynamically — all with the right features enabled.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

  - [Global Settings](#global-settings)
    - [Set Global Premium Proxy and JS Rendering](#set-global-premium-proxy-and-js-rendering)
    - [Override Global Settings for Specific Requests](#override-global-settings-for-specific-requests)
    - [Other Request Parameters](#other-request-parameters)
    - [Using Custom Headers](#using-custom-headers)
    - [Adding the Cookies Header](#adding-the-cookies-header)

- [New in v1.1.0](#new-in-v110)
  - [Retry Middleware](#retry-middleware)
  - [New Parameters](#new-parameters)
  - [Parameter Reference](#parameter-reference)

- [Usage Examples](#usage-examples)

## Installation

```bash
pip install scrapy-zenrows-middleware
```

## Usage

- Sign up for free on [ZenRows](https://www.zenrows.com/) to open the Request Builder and copy your ZenRows API key and implement the middleware.

### Global Settings

- Add the ZenRows Scraper API middleware to your `DOWNLOADER_MIDDLEWARE` and specify your ZenRows API Key:

_settings.py_

```python
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zenrows.ZenRowsMiddleware": 543,
}

# ZenRows API Key
ZENROWS_API_KEY = "<YOUR_ZENROWS_API_KEY>"
```

#### Set Global Premium Proxy and JS Rendering

The middleware will not use premium proxy and JS rendering by default. So, `USE_ZENROWS_PREMIUM_PROXY` and `USE_ZENROWS_JS_RENDER` are `False` by default. To turn on premium proxy and JS rendering globally, set both parameters to `True`:

_settings.py_

```python
# ...

USE_ZENROWS_PREMIUM_PROXY = True # to turn on premium proxy (False by default)
USE_ZENROWS_JS_RENDER = True # to turn on JS rendering (False by default)
```

### Override Global Settings for Specific Requests

If you have multiple spiders and don't want to apply global premium proxy and JS rendering for all, you can apply the middleware to specific ones by using `ZenRowsRequest` in `start_requests`.

`ZenRowsRequest` accepts the URL, request params, and headers options.

For example, to set Premium Proxy and JS Rendering for a specific request:

```python
# pip install scrapy-zenrows-middleware
from scrapy_zenrows import ZenRowsRequest

class YourSpider(scrapy.Spider):
    # ...

    def start_requests(self):
        # use ZenRowsRequest for customization
        for url in self.start_urls:
            yield ZenRowsRequest(
                url=url,
                # overrides the settings config for this specific spider
                params={
                    "js_render": "true",  # enable JavaScript rendering (if needed)
                    "premium_proxy": "true",  # use the proxy (if needed)
                },
            )

    def parse(self, response):
        # ...
```

#### Other Request Parameters

In addition to `js_render` and `premium_proxy`, the `ZenRowsRequest` accepts other parameters accepted by the ZenRows Scraper API:

```python
# ...
class YourSpider(scrapy.Spider):
    # ...

    def start_requests(self):
        # use ZenRowsRequest for customization
        for url in self.start_urls:
            yield ZenRowsRequest(
                url=url,
                params={
                    # ...,
                    "proxy_country": "ca", # use proxy from a specific country
                    "js_instructions": '[{"wait": 500}]', # pass JS instructions
                    "autparse": "true", # for supported websites
                    "outputs": "tables" # extract specific data,
                    'css_extractor': '{"links":"a @href","images":"img @src"}'
                    ""
                },
            )
```

For more information and supported parameters, check out our [Scraper API features](https://docs.zenrows.com/scraper-api/features/).

#### Using Custom Headers

You must set the `custom_headers` parameter to true in your request to use customized headers. This tells ZenRows to include your custom headers while managing critical browser-based headers.

For example, the following adds the referer header:

```python
# ...
class YourSpider(scrapy.Spider):
    # ...

    def start_requests(self):
        # use ZenRowsRequest for customization
        for url in self.start_urls:
            yield ZenRowsRequest(
                url=url,
                # overrides the settings config for this specific spider
                params={
                    "custom_headers": "true",  # to use custom headers
                },
                # add a referer header
                headers={
                    "Referer": "https://www.google.com/",
                },
            )
```

#### Adding the Cookies Header

Pass Cookies as a meta parameter (separated from the `headers`) just as specified by Scrapy. However, `custome_headers` must also be set to true.

```python
# ...
class YourSpider(scrapy.Spider):
    # ...

    def start_requests(self):
        # use ZenRowsRequest for customization
        for url in self.start_urls:
            yield ZenRowsRequest(
                url=url,
                # overrides the settings config for this specific spider
                params={
                    "custom_headers": "true",  # to use custom headers
                },
                cookies={
                    "currency": "USD",
                    "country": "UY",
                },
            )
```

Check our [headers feature](https://docs.zenrows.com/scraper-api/features/headers) for more information on the accepted request headers and how to set them.

---

## New in v1.1.0

### Retry Middleware

New `ZenRowsRetryMiddleware` with exponential backoff for robust scraping:

_settings.py_

```python
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zenrows.ZenRowsRetryMiddleware": 550,  # Add retry middleware
    "scrapy_zenrows.ZenRowsMiddleware": 543,
}

# Retry settings (all optional)
ZENROWS_RETRY_ENABLED = True  # Enable/disable retry (default: True)
ZENROWS_MAX_RETRIES = 3  # Max retry attempts (default: 3)
ZENROWS_RETRY_BACKOFF = 1.0  # Backoff factor in seconds (default: 1.0)
ZENROWS_RETRY_STATUS_CODES = [429, 500, 502, 503, 504]  # Status codes to retry
```

### New Parameters

#### Session Persistence (`session_id`)

Maintain the same IP address across multiple requests (up to 10 minutes):

```python
yield ZenRowsRequest(
    url="https://example.com/login",
    params={
        "session_id": 12345,  # Integer 1-99999
        "premium_proxy": "true",
    },
)
```

#### Wait for Element (`wait_for`)

Wait for a CSS selector to appear in DOM before returning (better than fixed `wait`):

```python
yield ZenRowsRequest(
    url="https://spa-example.com",
    params={
        "js_render": "true",
        "wait_for": ".product-list",  # Wait for this element
    },
)
```

#### Block Resources (`block_resources`)

Speed up scraping by blocking unnecessary resources:

```python
yield ZenRowsRequest(
    url="https://example.com",
    params={
        "js_render": "true",
        "block_resources": "image,media,font,stylesheet",
    },
)
```

#### Response Type (`response_type`)

Convert HTML to other formats for AI/LLM pipelines:

```python
yield ZenRowsRequest(
    url="https://blog.example.com/article",
    params={
        "response_type": "markdown",  # or "plaintext", "pdf"
    },
)
```

#### Original Status (`original_status`)

Get the original HTTP status code from the target page:

```python
yield ZenRowsRequest(
    url="https://example.com",
    params={
        "original_status": "true",
    },
)
```

#### Allowed Status Codes (`allowed_status_codes`)

Get content even from error pages:

```python
yield ZenRowsRequest(
    url="https://example.com/may-404",
    params={
        "allowed_status_codes": "404,500,503",
    },
)
```

### Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `js_render` | bool | Enable JavaScript rendering |
| `premium_proxy` | bool | Use residential IPs |
| `proxy_country` | str | Country code (us, de, jp) |
| `proxy_city` | str | City name (requires premium_proxy) |
| `session_id` | int | Maintain IP (1-99999, 10 min) |
| `wait` | int | Wait milliseconds after load |
| `wait_for` | str | Wait for CSS selector |
| `block_resources` | str | Block resources (image,media,font) |
| `js_instructions` | str | JSON array of JS actions |
| `autoparse` | bool | Auto-extract structured data |
| `css_extractor` | str | CSS selectors in JSON |
| `outputs` | str | Data types: tables,emails |
| `response_type` | str | markdown, plaintext, pdf |
| `json_response` | bool | Capture XHR/Fetch as JSON |
| `screenshot` | bool | Capture screenshot |
| `screenshot_fullpage` | bool | Full page screenshot |
| `screenshot_selector` | str | Screenshot specific element |
| `screenshot_format` | str | png or jpeg |
| `screenshot_quality` | int | JPEG quality 1-100 |
| `original_status` | bool | Return target's HTTP status |
| `allowed_status_codes` | str | Get content from error pages |
| `custom_headers` | bool | Enable custom headers |

---

## Usage Examples

Here are example spider demonstrating how to use the `scrapy_zenrows` middleware:

- **[antibot_bypass_spider](examples/zenrows_examples/spiders/antibot_bypass_spider.py)**: Demonstrates the basic usage of the ZenRows Scraper API for bypassing anti-bots.
- **[concurrent_ecommerce_spider](examples/zenrows_examples/spiders/concurrent_ecommerce_spider.py)**: Scraping concurrently with Scrapy while using `ZenRowsRequest`.
- **[custom_headers_spider](examples/zenrows_examples/spiders/custom_headers_spider.py)**: Shows how to specify custom headers, including Cookies while using `ZenRowsRequest`.
- **[pagination_spider](examples/zenrows_examples/spiders/pagination_spider.py)**: Shows how to implement pagination in Scrapy while using `ZenRowsRequest`.
- **[screenshot_spider](examples/zenrows_examples/spiders/screenshot_spider.py)**: Demonstrates how to add screenshot capability to Scrapy with the ZenRows Scraper API.
- **[table_parsing_spider](examples/zenrows_examples/spiders/table_parsing_spider.py)**: Examples showing how to parse a table using the `outputs` feature of the ZenRows Scraper API. Check the [supported outputs](https://docs.zenrows.com/scraper-api/features/output) for more information.

### New in v1.1.0

- **[session_spider](examples/zenrows_examples/spiders/session_spider.py)**: Multi-step session-based scraping with IP persistence using `session_id`.
- **[dynamic_content_spider](examples/zenrows_examples/spiders/dynamic_content_spider.py)**: Scraping SPAs and dynamic content using `wait_for`.
- **[optimized_spider](examples/zenrows_examples/spiders/optimized_spider.py)**: High-performance scraping with `block_resources`.
- **[ai_pipeline_spider](examples/zenrows_examples/spiders/ai_pipeline_spider.py)**: Extracting content for AI/LLM pipelines using `response_type`.

Examples directory: [examples/](examples/)

👉🏼 **[Official scrapy-zenrows integration documentation](https://docs.zenrows.com/scraping-api/integrations/scrapy)**

👉🏼 **[Full Feature Roadmap](../docs/ROADMAP.md)**
