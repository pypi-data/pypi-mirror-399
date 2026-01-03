"""
ZenRows Request class for Scrapy.

Compatible with Scrapy 2.0+
"""

import copy

from scrapy import Request


class ZenRowsRequest(Request):
    """
    Scrapy Request subclass for ZenRows Scraper API.

    Use this class instead of scrapy.Request when you want requests
    to be processed through ZenRows API.

    Args:
        url (str): Target URL to scrape
        params (dict, optional): ZenRows API parameters
        headers (dict, optional): Custom HTTP headers
        cookies (dict, optional): Request cookies
        meta (dict, optional): Scrapy request metadata
        *args, **kwargs: Additional Scrapy Request arguments

    ZenRows API Parameters (via params dict):

    Page Loading:
        js_render (bool|str): Enable JavaScript rendering with headless browser.
            Required for SPAs, dynamic content, and screenshot features.
        wait (int|str): Wait fixed milliseconds after page load.
            Example: "5000" for 5 seconds.
        wait_for (str): Wait for CSS selector to appear in DOM before returning.
            Essential for async-loading content. Example: ".main-content"
        block_resources (str): Block specific resources to speed up scraping.
            Comma-separated: "image,media,font,stylesheet,script"
        js_instructions (str): Execute custom JavaScript on page.
            JSON array of instructions. Example: '[{"click": ".btn"}, {"wait": 500}]'

    Proxy Settings:
        premium_proxy (bool|str): Use residential IPs to bypass anti-bot protection.
            Required for protected sites.
        proxy_country (str): Country code for proxy geolocation.
            Example: "us", "de", "jp"
        proxy_city (str): City name for granular geolocation.
            Requires premium_proxy=true. Example: "new york"
        session_id (int|str): Maintain same IP across requests (1-99999).
            Lasts up to 10 minutes. Essential for multi-step processes.

    Data Extraction:
        autoparse (bool|str): Auto-extract structured data from supported sites.
        css_extractor (str): Extract elements using CSS selectors.
            JSON format. Example: '{"title": "h1", "links": "a @href"}'
        outputs (str): Data types to extract from HTML.
            Comma-separated: "tables,hashtags,emails"
        response_type (str): Convert HTML to other formats.
            Options: "markdown", "plaintext", "pdf"
        json_response (bool|str): Capture network requests in JSON format.
            Returns XHR/Fetch data.

    Screenshots:
        screenshot (bool|str): Capture above-fold screenshot.
            Requires js_render=true.
        screenshot_fullpage (bool|str): Capture full page screenshot.
            Mutually exclusive with screenshot_selector.
        screenshot_selector (str): Screenshot specific element by CSS selector.
            Mutually exclusive with screenshot_fullpage.
        screenshot_format (str): Image format: "png" (default) or "jpeg"
        screenshot_quality (int|str): JPEG quality 1-100.
            Lower values reduce file size.

    Response Handling:
        original_status (bool|str): Return original HTTP status from target page.
            Useful for debugging.
        allowed_status_codes (str): Get content even on error status codes.
            Comma-separated. Example: "404,500,503"
        custom_headers (bool|str): Enable sending custom headers.
            Required when using custom Referer, User-Agent, etc.

    Example:
        >>> from scrapy_zenrows import ZenRowsRequest
        >>>
        >>> # Basic request with JS rendering
        >>> yield ZenRowsRequest(
        ...     url="https://example.com",
        ...     params={"js_render": "true", "premium_proxy": "true"},
        ...     callback=self.parse,
        ... )
        >>>
        >>> # Wait for dynamic content
        >>> yield ZenRowsRequest(
        ...     url="https://spa-example.com",
        ...     params={
        ...         "js_render": "true",
        ...         "wait_for": ".product-list",
        ...         "block_resources": "image,font",
        ...     },
        ...     callback=self.parse_products,
        ... )
        >>>
        >>> # Multi-step session with same IP
        >>> yield ZenRowsRequest(
        ...     url="https://example.com/login",
        ...     params={"session_id": 12345, "premium_proxy": "true"},
        ...     callback=self.after_login,
        ... )
        >>>
        >>> # Get markdown for AI processing
        >>> yield ZenRowsRequest(
        ...     url="https://blog.example.com/article",
        ...     params={"response_type": "markdown"},
        ...     callback=self.process_markdown,
        ... )
    """

    def __init__(
        self,
        url,
        params=None,
        headers=None,
        cookies=None,
        meta=None,
        **kwargs,
    ):
        meta = copy.deepcopy(meta) or {}
        self.params = params or {}

        super().__init__(
            url,
            headers=headers,
            cookies=cookies,
            meta=meta,
            **kwargs,
        )
