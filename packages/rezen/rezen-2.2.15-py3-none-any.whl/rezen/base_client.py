"""Base client for ReZEN API."""

import os
import time
from typing import Any, Dict, List, Optional, Union

import requests

from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RezenError,
    ServerError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://arrakis.therealbrokerage.com/api/v1"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RETRIES = 0
DEFAULT_RETRY_BACKOFF_SECONDS = 0.5

ENV_TIMEOUT_SECONDS = "REZEN_TIMEOUT_SECONDS"
ENV_MAX_RETRIES = "REZEN_MAX_RETRIES"
ENV_RETRY_BACKOFF_SECONDS = "REZEN_RETRY_BACKOFF_SECONDS"


def _parse_env_float(env_var: str, default: float) -> float:
    """Parse an environment variable as float.

    Args:
        env_var: Environment variable name.
        default: Default value to use when missing/invalid.

    Returns:
        Parsed float value.
    """
    raw = os.getenv(env_var)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _parse_env_int(env_var: str, default: int) -> int:
    """Parse an environment variable as int.

    Args:
        env_var: Environment variable name.
        default: Default value to use when missing/invalid.

    Returns:
        Parsed int value.
    """
    raw = os.getenv(env_var)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class BaseClient:
    """Base client for ReZEN API with common functionality."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        *,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
    ) -> None:
        """Initialize the base client.

        Args:
            api_key: API key for authentication. If None, will look for
                REZEN_API_KEY env var
            base_url: Base URL for the API. Defaults to production URL
            timeout_seconds: Default request timeout in seconds. If None, will look
                for REZEN_TIMEOUT_SECONDS env var (default: 30 seconds).
            max_retries: Maximum number of retries for transient failures. If None,
                will look for REZEN_MAX_RETRIES env var (default: 0).
            retry_backoff_seconds: Base backoff in seconds between retries. If None,
                will look for REZEN_RETRY_BACKOFF_SECONDS env var (default: 0.5).
        """
        self.api_key = api_key or os.getenv("REZEN_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set REZEN_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout_seconds = (
            float(timeout_seconds)
            if timeout_seconds is not None
            else _parse_env_float(ENV_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS)
        )
        self.max_retries = (
            int(max_retries)
            if max_retries is not None
            else _parse_env_int(ENV_MAX_RETRIES, DEFAULT_MAX_RETRIES)
        )
        self.retry_backoff_seconds = (
            float(retry_backoff_seconds)
            if retry_backoff_seconds is not None
            else _parse_env_float(
                ENV_RETRY_BACKOFF_SECONDS, DEFAULT_RETRY_BACKOFF_SECONDS
            )
        )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            Various RezenError subclasses based on status code
        """
        if response.status_code == 204:
            return {}

        try:
            response_data: Any = response.json() if response.content else {}
        except ValueError:
            response_data = {"message": response.text}

        if response.status_code in (200, 201):
            return response_data

        error_payload: Dict[str, Any]
        if isinstance(response_data, dict):
            error_payload = response_data
        else:
            error_payload = {"message": str(response_data), "raw": response_data}

        if response.status_code == 400:
            error_message = str(error_payload.get("message", "Invalid request"))
            # Add more context for common errors
            if "Invalid request" in error_message and "/owner-info" in response.url:
                error_message += (
                    " (Note: Owner agent endpoint requires proper transaction setup. "
                    "See TransactionSequenceError for required steps.)"
                )
            raise ValidationError(
                f"Bad request: {error_message}",
                status_code=400,
                response_data=error_payload,
            )
        elif response.status_code == 401:
            message = str(error_payload.get("message", "Invalid credentials"))
            raise AuthenticationError(
                f"Authentication failed: {message}",
                status_code=401,
                response_data=error_payload,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                f"Resource not found: {error_payload.get('message', 'Not found')}",
                status_code=404,
                response_data=error_payload,
            )
        elif response.status_code == 429:
            message = str(error_payload.get("message", "Too many requests"))
            raise RateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=429,
                response_data=error_payload,
            )
        elif 500 <= response.status_code < 600:
            message = str(error_payload.get("message", "Internal server error"))
            raise ServerError(
                f"Server error: {message}",
                status_code=response.status_code,
                response_data=error_payload,
            )
        else:
            raise RezenError(
                f"Unexpected error: {error_payload.get('message', 'Unknown error')}",
                status_code=response.status_code,
                response_data=error_payload,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Form data to send
            json_data: JSON data to send (can be dict or list)
            files: Files to upload
            params: Query parameters
            timeout_seconds: Optional per-request timeout override in seconds.

        Returns:
            Parsed response data

        Raises:
            NetworkError: When network connection fails
            Various RezenError subclasses: Based on response status
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        effective_timeout = (
            float(timeout_seconds)
            if timeout_seconds is not None
            else self.timeout_seconds
        )

        retryable_status_codes = {500, 502, 503, 504}

        for attempt in range(self.max_retries + 1):
            try:
                # Don't send json parameter if files are present
                if files:
                    # Don't set Content-Type for multipart requests; let requests handle it.
                    # Preserve our required X-API-KEY authentication header.
                    final_headers = {
                        "X-API-KEY": self.api_key,
                        "Accept": "application/json",
                    }
                    response = requests.request(
                        method=method,
                        url=url,
                        data=data,
                        files=files,
                        params=params,
                        headers=final_headers,
                        timeout=effective_timeout,
                    )
                else:
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=json_data,
                        data=data,
                        params=params,
                        timeout=effective_timeout,
                    )

                if (
                    response.status_code in retryable_status_codes
                    and attempt < self.max_retries
                ):
                    time.sleep(self.retry_backoff_seconds * (2**attempt))
                    continue

                return self._handle_response(response)

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_seconds * (2**attempt))
                    continue
                raise NetworkError(f"Network error: {str(e)}") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Make GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            timeout_seconds: Optional per-request timeout override in seconds.

        Returns:
            Parsed response data
        """
        return self._request(
            "GET", endpoint, params=params, timeout_seconds=timeout_seconds
        )

    def post(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Make POST request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data to send (can be dict or list)
            data: Form data to send
            files: Files to upload
            timeout_seconds: Optional per-request timeout override in seconds.

        Returns:
            Parsed response data
        """
        return self._request(
            "POST",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )

    def put(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Make PUT request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data to send (can be dict or list)
            data: Form data to send
            files: Files to upload
            timeout_seconds: Optional per-request timeout override in seconds.

        Returns:
            Parsed response data
        """
        return self._request(
            "PUT",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )

    def delete(self, endpoint: str, *, timeout_seconds: Optional[float] = None) -> Any:
        """Make DELETE request.

        Args:
            endpoint: API endpoint path
            timeout_seconds: Optional per-request timeout override in seconds.

        Returns:
            Parsed response data
        """
        return self._request("DELETE", endpoint, timeout_seconds=timeout_seconds)

    def patch(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Make PATCH request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data to send (can be dict or list)
            data: Form data to send
            files: Files to upload
            timeout_seconds: Optional per-request timeout override in seconds.

        Returns:
            Parsed response data
        """
        return self._request(
            "PATCH",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )
