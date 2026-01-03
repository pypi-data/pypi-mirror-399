"""
Unit tests for ZenRowsRetryMiddleware.
"""

from unittest.mock import MagicMock, patch

import pytest
from scrapy.exceptions import NotConfigured
from scrapy.http import Request, Response
from scrapy.settings import Settings

from scrapy_zenrows import ZenRowsRetryMiddleware


class TestZenRowsRetryMiddlewareInit:
    """Tests for retry middleware initialization."""

    def test_init_with_defaults(self, retry_settings):
        """Test middleware initializes with default settings."""
        middleware = ZenRowsRetryMiddleware(retry_settings)

        assert middleware.max_retry_times == 3
        assert middleware.backoff_factor == 1.0
        assert 429 in middleware.retry_http_codes
        assert 500 in middleware.retry_http_codes

    def test_init_with_custom_settings(self, custom_retry_settings):
        """Test middleware initializes with custom settings."""
        middleware = ZenRowsRetryMiddleware(custom_retry_settings)

        assert middleware.max_retry_times == 5
        assert middleware.backoff_factor == 2.0
        assert 429 in middleware.retry_http_codes
        assert 502 not in middleware.retry_http_codes

    def test_init_disabled_raises_not_configured(self):
        """Test disabled middleware raises NotConfigured."""
        settings = Settings({"ZENROWS_RETRY_ENABLED": False})

        with pytest.raises(NotConfigured):
            ZenRowsRetryMiddleware(settings)

    def test_from_crawler(self, retry_settings):
        """Test from_crawler class method."""
        crawler = MagicMock()
        crawler.settings = retry_settings

        middleware = ZenRowsRetryMiddleware.from_crawler(crawler)

        assert isinstance(middleware, ZenRowsRetryMiddleware)


class TestZenRowsRetryMiddlewareBackoff:
    """Tests for exponential backoff calculation."""

    def test_backoff_time_first_retry(self, retry_settings):
        """Test backoff time for first retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)

        backoff = middleware._get_backoff_time(0)

        assert backoff == 1.0  # 1.0 * 2^0 = 1.0

    def test_backoff_time_second_retry(self, retry_settings):
        """Test backoff time for second retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)

        backoff = middleware._get_backoff_time(1)

        assert backoff == 2.0  # 1.0 * 2^1 = 2.0

    def test_backoff_time_third_retry(self, retry_settings):
        """Test backoff time for third retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)

        backoff = middleware._get_backoff_time(2)

        assert backoff == 4.0  # 1.0 * 2^2 = 4.0

    def test_backoff_time_with_custom_factor(self, custom_retry_settings):
        """Test backoff with custom factor."""
        middleware = ZenRowsRetryMiddleware(custom_retry_settings)

        backoff = middleware._get_backoff_time(1)

        assert backoff == 4.0  # 2.0 * 2^1 = 4.0


class TestZenRowsRetryMiddlewareProcessResponse:
    """Tests for process_response method."""

    def test_returns_response_on_success(self, retry_settings):
        """Test successful responses are returned."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        response = Response(url="https://example.com", status=200, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert result is response

    def test_returns_response_with_dont_retry(self, retry_settings):
        """Test responses with dont_retry meta are returned."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com", meta={"dont_retry": True})
        response = Response(url="https://example.com", status=429, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert result is response

    @patch("time.sleep")
    def test_retries_on_429(self, mock_sleep, retry_settings):
        """Test 429 status triggers retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        response = Response(url="https://example.com", status=429, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert isinstance(result, Request)
        assert result.meta.get("retry_times") == 1
        mock_sleep.assert_called_once()

    @patch("time.sleep")
    def test_retries_on_500(self, mock_sleep, retry_settings):
        """Test 500 status triggers retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        response = Response(url="https://example.com", status=500, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert isinstance(result, Request)
        assert result.meta.get("retry_times") == 1

    @patch("time.sleep")
    def test_max_retries_exceeded(self, mock_sleep, retry_settings):
        """Test response returned when max retries exceeded."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com", meta={"retry_times": 3})
        response = Response(url="https://example.com", status=429, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert result is response
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_retry_increments_count(self, mock_sleep, retry_settings):
        """Test retry count increments correctly."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com", meta={"retry_times": 1})
        response = Response(url="https://example.com", status=500, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert result.meta.get("retry_times") == 2

    def test_non_retry_status_not_retried(self, retry_settings):
        """Test non-retry status codes are not retried."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        response = Response(url="https://example.com", status=404, request=request)
        spider = MagicMock()

        result = middleware.process_response(request, response, spider)

        assert result is response


class TestZenRowsRetryMiddlewareProcessException:
    """Tests for process_exception method."""

    @patch("time.sleep")
    def test_retries_on_exception(self, mock_sleep, retry_settings):
        """Test exceptions trigger retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        exception = ConnectionError("Connection refused")
        spider = MagicMock()

        result = middleware.process_exception(request, exception, spider)

        assert isinstance(result, Request)
        assert result.meta.get("retry_times") == 1
        mock_sleep.assert_called_once()

    def test_no_retry_with_dont_retry(self, retry_settings):
        """Test dont_retry prevents exception retry."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com", meta={"dont_retry": True})
        exception = ConnectionError("Connection refused")
        spider = MagicMock()

        result = middleware.process_exception(request, exception, spider)

        assert result is None

    @patch("time.sleep")
    def test_max_retries_exceeded_exception(self, mock_sleep, retry_settings):
        """Test None returned when max retries exceeded on exception."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com", meta={"retry_times": 3})
        exception = ConnectionError("Connection refused")
        spider = MagicMock()

        result = middleware.process_exception(request, exception, spider)

        assert result is None
        mock_sleep.assert_not_called()


class TestZenRowsRetryMiddlewareRetryMethod:
    """Tests for _retry helper method."""

    def test_retry_creates_new_request(self, retry_settings):
        """Test _retry creates a new request."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        spider = MagicMock()

        result = middleware._retry(request, "test reason", spider)

        assert isinstance(result, Request)
        assert result is not request

    def test_retry_sets_dont_filter(self, retry_settings):
        """Test retry request has dont_filter=True."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com")
        spider = MagicMock()

        result = middleware._retry(request, "test reason", spider)

        assert result.dont_filter is True

    def test_retry_adjusts_priority(self, retry_settings):
        """Test retry request has adjusted priority."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com", priority=10)
        spider = MagicMock()

        result = middleware._retry(request, "test reason", spider)

        assert result.priority == 9  # Default adjustment is -1

    def test_retry_preserves_url(self, retry_settings):
        """Test retry request preserves URL."""
        middleware = ZenRowsRetryMiddleware(retry_settings)
        request = Request(url="https://example.com/path?query=1")
        spider = MagicMock()

        result = middleware._retry(request, "test reason", spider)

        assert result.url == "https://example.com/path?query=1"


class TestZenRowsRetryMiddlewareStatusCodes:
    """Tests for retry status code configuration."""

    def test_default_status_codes(self, retry_settings):
        """Test default retry status codes."""
        middleware = ZenRowsRetryMiddleware(retry_settings)

        expected = frozenset([429, 500, 502, 503, 504])
        assert middleware.retry_http_codes == expected

    def test_custom_status_codes(self):
        """Test custom retry status codes."""
        settings = Settings({
            "ZENROWS_RETRY_ENABLED": True,
            "ZENROWS_RETRY_STATUS_CODES": [429, 503],
        })
        middleware = ZenRowsRetryMiddleware(settings)

        assert 429 in middleware.retry_http_codes
        assert 503 in middleware.retry_http_codes
        assert 500 not in middleware.retry_http_codes
        assert 502 not in middleware.retry_http_codes

    def test_empty_status_codes(self):
        """Test empty retry status codes list."""
        settings = Settings({
            "ZENROWS_RETRY_ENABLED": True,
            "ZENROWS_RETRY_STATUS_CODES": [],
        })
        middleware = ZenRowsRetryMiddleware(settings)

        assert len(middleware.retry_http_codes) == 0
