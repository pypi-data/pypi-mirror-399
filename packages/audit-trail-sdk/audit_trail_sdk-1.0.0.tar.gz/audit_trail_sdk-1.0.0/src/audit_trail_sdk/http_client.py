"""HTTP client for Audit Trail API"""

from typing import Any, Dict, Optional

import httpx

from .exceptions import AuditTrailApiError, AuditTrailConnectionError
from .retry import with_retry, with_retry_sync


class HttpClient:
    """HTTP client for Audit Trail API"""

    def __init__(
        self,
        server_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self._headers = headers or {}

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            **self._headers,
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        if not response.is_success:
            raise AuditTrailApiError(
                f"API request failed: {response.status_code}",
                response.status_code,
                response.text,
            )
        return response.json()

    # Sync methods
    def post_sync(self, path: str, body: Dict[str, Any]) -> Any:
        """POST request with retry (sync)"""
        return with_retry_sync(
            lambda: self._post_sync(path, body),
            self.retry_attempts,
            self.retry_delay,
        )

    def _post_sync(self, path: str, body: Dict[str, Any]) -> Any:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.server_url}{path}",
                    json=body,
                    headers=self._get_headers(),
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise AuditTrailConnectionError(f"Connection failed: {e}", e)

    def get_sync(self, path: str) -> Any:
        """GET request with retry (sync)"""
        return with_retry_sync(
            lambda: self._get_sync(path),
            self.retry_attempts,
            self.retry_delay,
        )

    def _get_sync(self, path: str) -> Any:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.server_url}{path}",
                    headers=self._get_headers(),
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise AuditTrailConnectionError(f"Connection failed: {e}", e)

    # Async methods
    async def post(self, path: str, body: Dict[str, Any]) -> Any:
        """POST request with retry (async)"""
        return await with_retry(
            lambda: self._post(path, body),
            self.retry_attempts,
            self.retry_delay,
        )

    async def _post(self, path: str, body: Dict[str, Any]) -> Any:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.server_url}{path}",
                    json=body,
                    headers=self._get_headers(),
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise AuditTrailConnectionError(f"Connection failed: {e}", e)

    async def get(self, path: str) -> Any:
        """GET request with retry (async)"""
        return await with_retry(
            lambda: self._get(path),
            self.retry_attempts,
            self.retry_delay,
        )

    async def _get(self, path: str) -> Any:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.server_url}{path}",
                    headers=self._get_headers(),
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise AuditTrailConnectionError(f"Connection failed: {e}", e)
