"""
Unit tests for ZenRowsMiddleware.
"""


from scrapy_zenrows import ZenRowsMiddleware


class TestZenRowsMiddlewareInit:
    """Tests for middleware initialization."""

    def test_init_with_api_key(self, api_key):
        """Test middleware initializes with API key."""
        middleware = ZenRowsMiddleware(api_key=api_key)

        assert middleware.api_key == api_key
        assert middleware.zenrows_url == "https://api.zenrows.com/v1"
        assert middleware.use_proxy is False
        assert middleware.js_render is False

    def test_init_with_all_options(self, api_key):
        """Test middleware initializes with all options."""
        middleware = ZenRowsMiddleware(
            api_key=api_key,
            use_proxy=True,
            js_render=True,
            original_status=True,
            session_id=12345,
            block_resources="image,font",
            allowed_status_codes="404,500",
        )

        assert middleware.use_proxy is True
        assert middleware.js_render is True
        assert middleware.original_status is True
        assert middleware.session_id == 12345
        assert middleware.block_resources == "image,font"
        assert middleware.allowed_status_codes == "404,500"


class TestZenRowsMiddlewareUrlBuilding:
    """Tests for API URL building."""

    def test_basic_url(self, api_key):
        """Test basic URL generation."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=False,
        )

        assert "api.zenrows.com" in url
        assert f"apikey={api_key}" in url
        assert "url=https%3A%2F%2Fexample.com" in url

    def test_url_with_premium_proxy(self, api_key):
        """Test URL with premium proxy enabled."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=True,
            js_render=False,
        )

        assert "premium_proxy=true" in url

    def test_url_with_js_render(self, api_key):
        """Test URL with JS rendering enabled."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=True,
        )

        assert "js_render=true" in url

    def test_url_with_session_id(self, api_key):
        """Test URL with session ID."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=False,
            session_id=12345,
        )

        assert "session_id=12345" in url

    def test_url_with_block_resources(self, api_key):
        """Test URL with block resources."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=False,
            block_resources="image,font,media",
        )

        assert "block_resources=" in url

    def test_url_with_original_status(self, api_key):
        """Test URL with original status."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=False,
            original_status=True,
        )

        assert "original_status=true" in url

    def test_url_with_allowed_status_codes(self, api_key):
        """Test URL with allowed status codes."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=False,
            allowed_status_codes="404,500,503",
        )

        assert "allowed_status_codes=" in url

    def test_url_with_custom_params(self, api_key):
        """Test URL with custom params passed through."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={
                "wait_for": ".content",
                "css_extractor": '{"title": "h1"}',
                "response_type": "markdown",
            },
            use_proxy=False,
            js_render=False,
        )

        assert "wait_for=" in url
        assert "css_extractor=" in url
        assert "response_type=markdown" in url

    def test_url_with_all_new_params(self, api_key):
        """Test URL with all v1.1.0 parameters."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={
                "wait_for": ".product-list",
                "proxy_city": "new york",
                "screenshot_selector": "#main",
                "response_type": "markdown",
            },
            use_proxy=True,
            js_render=True,
            original_status=True,
            session_id=99999,
            block_resources="image,media,font",
            allowed_status_codes="404,500",
        )

        assert "premium_proxy=true" in url
        assert "js_render=true" in url
        assert "original_status=true" in url
        assert "session_id=99999" in url
        assert "block_resources=" in url
        assert "allowed_status_codes=" in url
        assert "wait_for=" in url
        assert "response_type=markdown" in url


class TestZenRowsMiddlewareValidation:
    """Tests for parameter validation."""

    def test_validate_session_id_valid(self, api_key, caplog):
        """Test valid session ID passes validation."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({"session_id": 12345})

        assert "session_id must be" not in caplog.text

    def test_validate_session_id_too_high(self, api_key, caplog):
        """Test session ID > 99999 logs warning."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({"session_id": 100000})

        assert "session_id must be between 1 and 99999" in caplog.text

    def test_validate_session_id_too_low(self, api_key, caplog):
        """Test session ID < 1 logs warning."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({"session_id": 0})

        assert "session_id must be between 1 and 99999" in caplog.text

    def test_validate_screenshot_mutual_exclusion(self, api_key, caplog):
        """Test screenshot_selector and screenshot_fullpage mutual exclusion."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({
            "screenshot_selector": "#main",
            "screenshot_fullpage": "true",
        })

        assert "mutually exclusive" in caplog.text

    def test_validate_proxy_city_requires_premium(self, api_key, caplog):
        """Test proxy_city requires premium_proxy."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({"proxy_city": "new york"})

        assert "proxy_city requires premium_proxy=true" in caplog.text

    def test_validate_proxy_city_with_premium(self, api_key, caplog):
        """Test proxy_city with premium_proxy passes."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({
            "proxy_city": "new york",
            "premium_proxy": "true",
        })

        assert "proxy_city requires premium_proxy=true" not in caplog.text

    def test_validate_screenshot_requires_js_render(self, api_key, caplog):
        """Test screenshot requires js_render."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({"screenshot": "true"})

        assert "screenshot requires js_render=true" in caplog.text

    def test_validate_screenshot_with_js_render(self, api_key, caplog):
        """Test screenshot with js_render passes."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        middleware._validate_params({
            "screenshot": "true",
            "js_render": "true",
        })

        assert "screenshot requires js_render=true" not in caplog.text


class TestZenRowsMiddlewareBoolParam:
    """Tests for boolean parameter handling."""

    def test_bool_param_with_string_true(self, api_key):
        """Test string 'true' is converted to True."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        result = middleware._get_bool_param({"key": "true"}, "key", False)

        assert result is True

    def test_bool_param_with_string_false(self, api_key):
        """Test string 'false' is converted to False."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        result = middleware._get_bool_param({"key": "false"}, "key", True)

        assert result is False

    def test_bool_param_with_python_bool(self, api_key):
        """Test Python bool is passed through."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        result = middleware._get_bool_param({"key": True}, "key", False)

        assert result is True

    def test_bool_param_missing_uses_default(self, api_key):
        """Test missing key uses default."""
        middleware = ZenRowsMiddleware(api_key=api_key)
        result = middleware._get_bool_param({}, "key", True)

        assert result is True

    def test_bool_param_case_insensitive(self, api_key):
        """Test string comparison is case insensitive."""
        middleware = ZenRowsMiddleware(api_key=api_key)

        assert middleware._get_bool_param({"key": "TRUE"}, "key", False) is True
        assert middleware._get_bool_param({"key": "True"}, "key", False) is True
        assert middleware._get_bool_param({"key": "FALSE"}, "key", True) is False
