"""
ZenRows Scrapy Middleware.

Compatible with Scrapy 2.0+
"""

import logging
from urllib.parse import urlencode

from scrapy import Request
from scrapy.exceptions import NotConfigured

from .api_key_handler import HideApiKeyHandler
from .zenrows_request import ZenRowsRequest


class ZenRowsMiddleware:
    """
    Scrapy downloader middleware for ZenRows Scraper API.

    This middleware intercepts ZenRowsRequest objects and transforms them
    into API calls to ZenRows, handling authentication, proxy settings,
    and all API parameters.

    Required Settings:
        ZENROWS_API_KEY (str): Your ZenRows API key

    Optional Global Settings:
        USE_ZENROWS_PREMIUM_PROXY (bool): Enable premium proxies globally. Default: False
        USE_ZENROWS_JS_RENDER (bool): Enable JS rendering globally. Default: False
        USE_ZENROWS_ORIGINAL_STATUS (bool): Return original HTTP status. Default: False
        ZENROWS_SESSION_ID (int): Session ID for IP persistence (1-99999). Default: None
        ZENROWS_BLOCK_RESOURCES (str): Resources to block (comma-separated). Default: None
        ZENROWS_ALLOWED_STATUS_CODES (str): Status codes to allow (comma-separated). Default: None

    Usage in settings.py:
        DOWNLOADER_MIDDLEWARES = {
            "scrapy_zenrows.ZenRowsMiddleware": 543,
        }

        ZENROWS_API_KEY = "your_api_key"
        USE_ZENROWS_PREMIUM_PROXY = True
        USE_ZENROWS_JS_RENDER = True
    """

    def __init__(
        self,
        api_key,
        use_proxy=False,
        js_render=False,
        original_status=False,
        session_id=None,
        block_resources=None,
        allowed_status_codes=None,
    ):
        self.api_key = api_key
        self.zenrows_url = "https://api.zenrows.com/v1"
        self.use_proxy = use_proxy
        self.js_render = js_render
        self.original_status = original_status
        self.session_id = session_id
        self.block_resources = block_resources
        self.allowed_status_codes = allowed_status_codes
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get("ZENROWS_API_KEY")
        if not api_key:
            raise NotConfigured("ZenRows API Key is not configured")

        use_proxy = crawler.settings.getbool("USE_ZENROWS_PREMIUM_PROXY", False)
        js_render = crawler.settings.getbool("USE_ZENROWS_JS_RENDER", False)
        original_status = crawler.settings.getbool("USE_ZENROWS_ORIGINAL_STATUS", False)

        # Handle optional int setting (None if not set)
        session_id_raw = crawler.settings.get("ZENROWS_SESSION_ID")
        session_id = int(session_id_raw) if session_id_raw is not None else None

        block_resources = crawler.settings.get("ZENROWS_BLOCK_RESOURCES")
        allowed_status_codes = crawler.settings.get("ZENROWS_ALLOWED_STATUS_CODES")

        # Add ZenRows to allowed domains by default
        spider = crawler.spider
        try:
            if spider.allowed_domains and "api.zenrows.com" not in spider.allowed_domains:
                spider.allowed_domains.append("api.zenrows.com")
        except Exception:
            pass

        cls.set_up_logging(crawler)

        return cls(
            api_key=api_key,
            use_proxy=use_proxy,
            js_render=js_render,
            original_status=original_status,
            session_id=session_id,
            block_resources=block_resources,
            allowed_status_codes=allowed_status_codes,
        )

    @staticmethod
    def set_up_logging(crawler):
        formatter = HideApiKeyHandler("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(formatter)

    def process_request(self, request, spider):
        """
        Process outgoing ZenRowsRequest and transform to API URL.

        Args:
            request: The request object
            spider: The spider making the request

        Returns:
            Transformed Request with ZenRows API URL, or None for non-ZenRowsRequest
        """
        if isinstance(request, ZenRowsRequest):
            # Validate parameters
            self._validate_params(request.params)

            # Get parameter values (request params override global settings)
            use_proxy = self._get_bool_param(request.params, "premium_proxy", self.use_proxy)
            js_render = self._get_bool_param(request.params, "js_render", self.js_render)
            original_status = self._get_bool_param(request.params, "original_status", self.original_status)
            session_id = request.params.get("session_id", self.session_id)
            block_resources = request.params.get("block_resources", self.block_resources)
            allowed_status_codes = request.params.get("allowed_status_codes", self.allowed_status_codes)

            api_url = self.get_zenrows_api_url(
                url=request.url,
                params=request.params,
                use_proxy=use_proxy,
                js_render=js_render,
                original_status=original_status,
                session_id=session_id,
                block_resources=block_resources,
                allowed_status_codes=allowed_status_codes,
            )

            new_request = request.replace(
                cls=Request,
                url=api_url,
                meta=request.meta,
            )

            return new_request

    def process_response(self, request, response, spider):
        """
        Process response from ZenRows API.

        Args:
            request: The request that generated this response
            response: The response received
            spider: The spider making the request

        Returns:
            Response object
        """
        # Check if this is an allowed status code (don't log as error)
        allowed_codes = request.meta.get("zenrows_allowed_status_codes", "")
        if allowed_codes:
            allowed_list = [int(c.strip()) for c in allowed_codes.split(",") if c.strip()]
            if response.status in allowed_list:
                return response

        if response.status == 401:
            self.logger.error("Unauthorized: Invalid ZenRows API key provided.")
        elif response.status >= 400:
            try:
                error_response = response.json()
                error_title = error_response.get("title", "No title found")
            except Exception:
                error_title = "Unknown Error"
            self.logger.error(f"Error {response.status}: {error_title}")

        return response

    def get_zenrows_api_url(
        self,
        url,
        params,
        use_proxy,
        js_render,
        original_status=False,
        session_id=None,
        block_resources=None,
        allowed_status_codes=None,
    ):
        """
        Build the ZenRows API URL with all parameters.

        Args:
            url: Target URL to scrape
            params: Additional ZenRows parameters from request
            use_proxy: Enable premium proxy
            js_render: Enable JavaScript rendering
            original_status: Return original HTTP status code
            session_id: Session ID for IP persistence
            block_resources: Resources to block
            allowed_status_codes: Status codes to allow

        Returns:
            Complete ZenRows API URL
        """
        payload = {"url": url}

        # Core settings
        if use_proxy:
            payload["premium_proxy"] = "true"
        if js_render:
            payload["js_render"] = "true"
        if original_status:
            payload["original_status"] = "true"

        # Session management
        if session_id is not None:
            payload["session_id"] = str(session_id)

        # Resource blocking
        if block_resources:
            payload["block_resources"] = block_resources

        # Allowed status codes
        if allowed_status_codes:
            payload["allowed_status_codes"] = allowed_status_codes

        # Merge remaining request params (excluding already-processed ones)
        processed_params = {"premium_proxy", "js_render", "original_status", "session_id", "block_resources", "allowed_status_codes"}
        for key, value in params.items():
            if key not in processed_params:
                payload[key] = value

        api_url = f"{self.zenrows_url}/?apikey={self.api_key}&{urlencode(payload)}"
        return api_url

    def _get_bool_param(self, params, key, default):
        """
        Get boolean parameter value from params dict or default.

        Handles both Python bools and string "true"/"false" values.

        Args:
            params: Request params dict
            key: Parameter key
            default: Default value if not in params

        Returns:
            Boolean value
        """
        if key not in params:
            return default

        value = params[key]
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)

    def _validate_params(self, params):
        """
        Validate ZenRows request parameters.

        Logs warnings for invalid parameter combinations.

        Args:
            params: Request params dict
        """
        # Validate session_id range
        session_id = params.get("session_id")
        if session_id is not None:
            try:
                sid = int(session_id)
                if sid < 1 or sid > 99999:
                    self.logger.warning(f"session_id must be between 1 and 99999, got {sid}")
            except (ValueError, TypeError):
                self.logger.warning(f"session_id must be an integer, got {session_id}")

        # Validate screenshot_selector and screenshot_fullpage mutual exclusion
        has_selector = params.get("screenshot_selector")
        has_fullpage = self._get_bool_param(params, "screenshot_fullpage", False)
        if has_selector and has_fullpage:
            self.logger.warning("screenshot_selector and screenshot_fullpage are mutually exclusive. screenshot_selector will take precedence.")

        # Validate proxy_city requires premium_proxy
        proxy_city = params.get("proxy_city")
        premium_proxy = self._get_bool_param(params, "premium_proxy", False)
        if proxy_city and not premium_proxy:
            self.logger.warning("proxy_city requires premium_proxy=true. Enable premium_proxy for city-level geolocation.")

        # Validate screenshot requires js_render
        screenshot = self._get_bool_param(params, "screenshot", False)
        js_render = self._get_bool_param(params, "js_render", False)
        if screenshot and not js_render:
            self.logger.warning("screenshot requires js_render=true. Enable js_render for screenshot functionality.")
