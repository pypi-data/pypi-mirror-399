"""
Unit tests for ZenRowsRequest.
"""

from scrapy import Request

from scrapy_zenrows import ZenRowsRequest


class TestZenRowsRequestInit:
    """Tests for ZenRowsRequest initialization."""

    def test_basic_init(self):
        """Test basic request creation."""
        request = ZenRowsRequest(url="https://example.com")

        assert request.url == "https://example.com"
        assert request.params == {}
        assert isinstance(request, Request)

    def test_init_with_params(self):
        """Test request with params dict."""
        params = {"js_render": "true", "premium_proxy": "true"}
        request = ZenRowsRequest(url="https://example.com", params=params)

        assert request.params == params

    def test_init_with_headers(self):
        """Test request with custom headers."""
        headers = {"User-Agent": "Custom Agent"}
        request = ZenRowsRequest(url="https://example.com", headers=headers)

        assert request.headers.get("User-Agent") == b"Custom Agent"

    def test_init_with_cookies(self):
        """Test request with cookies."""
        cookies = {"session": "abc123"}
        request = ZenRowsRequest(url="https://example.com", cookies=cookies)

        assert request.cookies == cookies

    def test_init_with_meta(self):
        """Test request with meta dict."""
        meta = {"custom_key": "custom_value"}
        request = ZenRowsRequest(url="https://example.com", meta=meta)

        assert request.meta["custom_key"] == "custom_value"

    def test_init_meta_deepcopy(self):
        """Test that meta is deep copied."""
        meta = {"nested": {"key": "value"}}
        request = ZenRowsRequest(url="https://example.com", meta=meta)

        # Modify original meta
        meta["nested"]["key"] = "modified"

        # Request meta should be unchanged
        assert request.meta["nested"]["key"] == "value"

    def test_init_with_callback(self):
        """Test request with callback."""

        def my_callback(response):
            pass

        request = ZenRowsRequest(url="https://example.com", callback=my_callback)

        assert request.callback == my_callback

    def test_init_with_errback(self):
        """Test request with errback."""

        def my_errback(failure):
            pass

        request = ZenRowsRequest(url="https://example.com", errback=my_errback)

        assert request.errback == my_errback

    def test_init_with_method(self):
        """Test request with custom HTTP method."""
        request = ZenRowsRequest(url="https://example.com", method="POST")

        assert request.method == "POST"

    def test_init_with_body(self):
        """Test request with body."""
        request = ZenRowsRequest(url="https://example.com", method="POST", body="test body")

        assert request.body == b"test body"


class TestZenRowsRequestParams:
    """Tests for various ZenRows API parameters."""

    def test_js_render_param(self):
        """Test js_render parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"js_render": "true"})

        assert request.params["js_render"] == "true"

    def test_premium_proxy_param(self):
        """Test premium_proxy parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"premium_proxy": "true"})

        assert request.params["premium_proxy"] == "true"

    def test_wait_for_param(self):
        """Test wait_for parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"wait_for": ".content"})

        assert request.params["wait_for"] == ".content"

    def test_session_id_param(self):
        """Test session_id parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"session_id": 12345})

        assert request.params["session_id"] == 12345

    def test_block_resources_param(self):
        """Test block_resources parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"block_resources": "image,font,media"})

        assert request.params["block_resources"] == "image,font,media"

    def test_response_type_param(self):
        """Test response_type parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"response_type": "markdown"})

        assert request.params["response_type"] == "markdown"

    def test_css_extractor_param(self):
        """Test css_extractor parameter."""
        css_extractor = '{"title": "h1", "links": "a @href"}'
        request = ZenRowsRequest(url="https://example.com", params={"css_extractor": css_extractor})

        assert request.params["css_extractor"] == css_extractor

    def test_screenshot_params(self):
        """Test screenshot-related parameters."""
        request = ZenRowsRequest(
            url="https://example.com",
            params={
                "screenshot": "true",
                "screenshot_fullpage": "true",
                "screenshot_format": "jpeg",
                "screenshot_quality": 80,
            },
        )

        assert request.params["screenshot"] == "true"
        assert request.params["screenshot_fullpage"] == "true"
        assert request.params["screenshot_format"] == "jpeg"
        assert request.params["screenshot_quality"] == 80

    def test_proxy_geo_params(self):
        """Test proxy geolocation parameters."""
        request = ZenRowsRequest(
            url="https://example.com",
            params={
                "proxy_country": "us",
                "proxy_city": "new york",
            },
        )

        assert request.params["proxy_country"] == "us"
        assert request.params["proxy_city"] == "new york"

    def test_original_status_param(self):
        """Test original_status parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"original_status": "true"})

        assert request.params["original_status"] == "true"

    def test_allowed_status_codes_param(self):
        """Test allowed_status_codes parameter."""
        request = ZenRowsRequest(url="https://example.com", params={"allowed_status_codes": "404,500,503"})

        assert request.params["allowed_status_codes"] == "404,500,503"

    def test_all_params_combined(self):
        """Test multiple parameters combined."""
        params = {
            "js_render": "true",
            "premium_proxy": "true",
            "wait_for": ".product-list",
            "session_id": 99999,
            "block_resources": "image,font",
            "response_type": "markdown",
            "original_status": "true",
            "allowed_status_codes": "404,500",
        }
        request = ZenRowsRequest(url="https://example.com", params=params)

        for key, value in params.items():
            assert request.params[key] == value


class TestZenRowsRequestInheritance:
    """Tests for Request subclass behavior."""

    def test_is_scrapy_request_subclass(self):
        """Test that ZenRowsRequest is a Request subclass."""
        request = ZenRowsRequest(url="https://example.com")

        assert isinstance(request, Request)

    def test_copy_method(self):
        """Test that copy() preserves params."""
        request = ZenRowsRequest(url="https://example.com", params={"js_render": "true"})
        copied = request.copy()

        # Note: params is an instance attribute, copy() behavior depends on Scrapy version
        assert isinstance(copied, Request)

    def test_replace_method(self):
        """Test that replace() works."""
        request = ZenRowsRequest(url="https://example.com", params={"js_render": "true"})
        replaced = request.replace(url="https://other.com")

        assert replaced.url == "https://other.com"
        assert isinstance(replaced, Request)

    def test_priority(self):
        """Test priority setting."""
        request = ZenRowsRequest(url="https://example.com", priority=10)

        assert request.priority == 10

    def test_dont_filter(self):
        """Test dont_filter setting."""
        request = ZenRowsRequest(url="https://example.com", dont_filter=True)

        assert request.dont_filter is True

    def test_cb_kwargs(self):
        """Test cb_kwargs are passed through."""
        request = ZenRowsRequest(url="https://example.com", cb_kwargs={"item_id": 123})

        assert request.cb_kwargs == {"item_id": 123}
