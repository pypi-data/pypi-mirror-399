"""Audit Trail SDK Client"""

from __future__ import annotations

from typing import Dict, List, Optional

from .exceptions import AuditTrailApiError
from .http_client import HttpClient
from .models import (
    BatchEventResponse,
    Event,
    EventResponse,
    SearchCriteria,
    SearchResult,
)


class AuditTrailClient:
    """Audit Trail SDK Client - supports both sync and async operations"""

    def __init__(
        self,
        server_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        self._http = HttpClient(
            server_url=server_url,
            api_key=api_key,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
            headers=headers,
        )

    # ========== SYNC METHODS ==========

    def log(self, event: Event) -> EventResponse:
        """Log a single event (sync)"""
        data = self._http.post_sync("/api/v1/events", event.model_dump(by_alias=True))
        return EventResponse(**data)

    def log_batch(self, events: List[Event]) -> BatchEventResponse:
        """Log multiple events (sync)"""
        body = {"events": [e.model_dump(by_alias=True) for e in events]}
        data = self._http.post_sync("/api/v1/events/batch", body)
        return BatchEventResponse(**data)

    def get_by_id(self, event_id: str) -> Optional[EventResponse]:
        """Get event by ID (sync)"""
        try:
            data = self._http.get_sync(f"/api/v1/events/{event_id}")
            return EventResponse(**data)
        except AuditTrailApiError as e:
            if e.status_code == 404:
                return None
            raise

    def search(self, criteria: SearchCriteria) -> SearchResult:
        """Search events (sync)"""
        data = self._http.post_sync(
            "/api/v1/search", criteria.model_dump(by_alias=True, exclude_none=True)
        )
        return SearchResult(**data)

    def quick_search(
        self,
        query: str,
        tenant_id: str,
        page: int = 0,
        size: int = 20,
    ) -> SearchResult:
        """Quick search events (sync)"""
        params = f"?q={query}&tenantId={tenant_id}&page={page}&size={size}"
        data = self._http.get_sync(f"/api/v1/search/quick{params}")
        return SearchResult(**data)

    # ========== ASYNC METHODS ==========

    async def log_async(self, event: Event) -> EventResponse:
        """Log a single event (async)"""
        data = await self._http.post("/api/v1/events", event.model_dump(by_alias=True))
        return EventResponse(**data)

    async def log_batch_async(self, events: List[Event]) -> BatchEventResponse:
        """Log multiple events (async)"""
        body = {"events": [e.model_dump(by_alias=True) for e in events]}
        data = await self._http.post("/api/v1/events/batch", body)
        return BatchEventResponse(**data)

    async def get_by_id_async(self, event_id: str) -> Optional[EventResponse]:
        """Get event by ID (async)"""
        try:
            data = await self._http.get(f"/api/v1/events/{event_id}")
            return EventResponse(**data)
        except AuditTrailApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def search_async(self, criteria: SearchCriteria) -> SearchResult:
        """Search events (async)"""
        data = await self._http.post(
            "/api/v1/search", criteria.model_dump(by_alias=True, exclude_none=True)
        )
        return SearchResult(**data)

    async def quick_search_async(
        self,
        query: str,
        tenant_id: str,
        page: int = 0,
        size: int = 20,
    ) -> SearchResult:
        """Quick search events (async)"""
        params = f"?q={query}&tenantId={tenant_id}&page={page}&size={size}"
        data = await self._http.get(f"/api/v1/search/quick{params}")
        return SearchResult(**data)

    # ========== BUILDER ==========

    @classmethod
    def builder(cls) -> "AuditTrailClientBuilder":
        """Create a client builder"""
        return AuditTrailClientBuilder()


class AuditTrailClientBuilder:
    """Builder for AuditTrailClient"""

    def __init__(self) -> None:
        self._server_url: Optional[str] = None
        self._api_key: Optional[str] = None
        self._timeout: float = 30.0
        self._retry_attempts: int = 3
        self._retry_delay: float = 1.0
        self._headers: Dict[str, str] = {}

    def server_url(self, url: str) -> "AuditTrailClientBuilder":
        """Set the server URL"""
        self._server_url = url
        return self

    def api_key(self, key: str) -> "AuditTrailClientBuilder":
        """Set the API key"""
        self._api_key = key
        return self

    def timeout(self, seconds: float) -> "AuditTrailClientBuilder":
        """Set the request timeout in seconds"""
        self._timeout = seconds
        return self

    def retry_attempts(self, attempts: int) -> "AuditTrailClientBuilder":
        """Set the number of retry attempts"""
        self._retry_attempts = attempts
        return self

    def retry_delay(self, seconds: float) -> "AuditTrailClientBuilder":
        """Set the initial retry delay in seconds"""
        self._retry_delay = seconds
        return self

    def headers(self, headers: Dict[str, str]) -> "AuditTrailClientBuilder":
        """Set custom headers"""
        self._headers = headers
        return self

    def build(self) -> AuditTrailClient:
        """Build the client"""
        if not self._server_url:
            raise ValueError("server_url is required")
        return AuditTrailClient(
            server_url=self._server_url,
            api_key=self._api_key,
            timeout=self._timeout,
            retry_attempts=self._retry_attempts,
            retry_delay=self._retry_delay,
            headers=self._headers,
        )
