"""
ZenRows Retry Middleware with exponential backoff.

Compatible with Scrapy 2.0+
"""

import logging
import time

from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message


class ZenRowsRetryMiddleware:
    """
    Retry middleware with exponential backoff for ZenRows API requests.

    This middleware adds:
    - Exponential backoff between retries
    - ZenRows-specific default status codes (429, 500, 502, 503, 504)
    - Configurable retry settings via Scrapy settings

    Settings:
        ZENROWS_RETRY_ENABLED (bool): Enable retry middleware. Default: True
        ZENROWS_MAX_RETRIES (int): Maximum number of retries. Default: 3
        ZENROWS_RETRY_BACKOFF (float): Base backoff factor in seconds. Default: 1.0
        ZENROWS_RETRY_STATUS_CODES (list): HTTP status codes to retry. Default: [429, 500, 502, 503, 504]

    Usage in settings.py:
        DOWNLOADER_MIDDLEWARES = {
            "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
            "scrapy_zenrows.ZenRowsMiddleware": 543,
        }

        ZENROWS_RETRY_ENABLED = True
        ZENROWS_MAX_RETRIES = 3
        ZENROWS_RETRY_BACKOFF = 1.0
        ZENROWS_RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
    """

    DEFAULT_RETRY_STATUS_CODES = frozenset([429, 500, 502, 503, 504])
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_FACTOR = 1.0

    def __init__(self, settings):
        if not settings.getbool("ZENROWS_RETRY_ENABLED", True):
            raise NotConfigured("ZenRows retry middleware is disabled")

        self.max_retry_times = settings.getint("ZENROWS_MAX_RETRIES", self.DEFAULT_MAX_RETRIES)
        self.backoff_factor = settings.getfloat("ZENROWS_RETRY_BACKOFF", self.DEFAULT_BACKOFF_FACTOR)
        retry_codes = settings.getlist("ZENROWS_RETRY_STATUS_CODES", list(self.DEFAULT_RETRY_STATUS_CODES))
        self.retry_http_codes = frozenset(int(x) for x in retry_codes)
        self.priority_adjust = settings.getint("RETRY_PRIORITY_ADJUST", -1)
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        """
        Process response and retry if status code matches retry codes.

        Args:
            request: The request that generated this response
            response: The response received
            spider: The spider making the request

        Returns:
            Response or Request (for retry)
        """
        if request.meta.get("dont_retry", False):
            return response

        if response.status in self.retry_http_codes:
            retry_times = request.meta.get("retry_times", 0)

            if retry_times < self.max_retry_times:
                backoff_time = self._get_backoff_time(retry_times)
                reason = response_status_message(response.status)
                self.logger.warning(f"ZenRows request failed with status {response.status}. Retrying in {backoff_time:.1f}s (attempt {retry_times + 1}/{self.max_retry_times}). Reason: {reason}")
                time.sleep(backoff_time)
                return self._retry(request, reason, spider) or response

            self.logger.error(f"ZenRows request failed after {self.max_retry_times} retries. Status: {response.status}")

        return response

    def process_exception(self, request, exception, spider):
        """
        Process exception and retry if appropriate.

        Args:
            request: The request that caused the exception
            exception: The exception raised
            spider: The spider making the request

        Returns:
            Request (for retry) or None
        """
        if request.meta.get("dont_retry", False):
            return None

        retry_times = request.meta.get("retry_times", 0)

        if retry_times < self.max_retry_times:
            backoff_time = self._get_backoff_time(retry_times)
            self.logger.warning(f"ZenRows request failed with exception: {exception}. Retrying in {backoff_time:.1f}s (attempt {retry_times + 1}/{self.max_retry_times})")
            time.sleep(backoff_time)
            return self._retry(request, exception, spider)

        self.logger.error(f"ZenRows request failed after {self.max_retry_times} retries. Exception: {exception}")
        return None

    def _retry(self, request, reason, spider):
        """
        Create a retry request with updated metadata.

        Args:
            request: Original request to retry
            reason: Reason for the retry
            spider: The spider making the request

        Returns:
            New request for retry
        """
        retry_times = request.meta.get("retry_times", 0) + 1
        self.logger.debug(f"Retrying {request.url} (failed {retry_times} times): {reason}")

        new_request = request.copy()
        new_request.meta["retry_times"] = retry_times
        new_request.dont_filter = True
        new_request.priority = request.priority + self.priority_adjust
        return new_request

    def _get_backoff_time(self, retry_times):
        """
        Calculate exponential backoff time.

        Args:
            retry_times: Number of retries so far

        Returns:
            Backoff time in seconds
        """
        return self.backoff_factor * (2**retry_times)
