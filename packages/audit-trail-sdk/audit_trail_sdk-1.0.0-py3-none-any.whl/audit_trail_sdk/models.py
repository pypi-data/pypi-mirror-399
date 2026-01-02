"""Pydantic models for Audit Trail SDK"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .types import ActorType


class Actor(BaseModel):
    """Represents an actor performing an action"""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: ActorType
    name: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = Field(default=None, serialization_alias="userAgent")
    attributes: Optional[Dict[str, str]] = None

    @classmethod
    def user(cls, id: str, name: Optional[str] = None) -> Actor:
        """Create a user actor"""
        return cls(id=id, type=ActorType.USER, name=name)

    @classmethod
    def system(cls, id: str) -> Actor:
        """Create a system actor"""
        return cls(id=id, type=ActorType.SYSTEM)

    @classmethod
    def service(cls, id: str, name: Optional[str] = None) -> Actor:
        """Create a service actor"""
        return cls(id=id, type=ActorType.SERVICE, name=name)


class Action(BaseModel):
    """Represents an action performed"""

    type: str
    description: Optional[str] = None
    category: Optional[str] = None

    @classmethod
    def create(cls, description: Optional[str] = None) -> Action:
        """Create a CREATE action"""
        return cls(type="CREATE", description=description)

    @classmethod
    def read(cls, description: Optional[str] = None) -> Action:
        """Create a READ action"""
        return cls(type="READ", description=description)

    @classmethod
    def update(cls, description: Optional[str] = None) -> Action:
        """Create an UPDATE action"""
        return cls(type="UPDATE", description=description)

    @classmethod
    def delete(cls, description: Optional[str] = None) -> Action:
        """Create a DELETE action"""
        return cls(type="DELETE", description=description)

    @classmethod
    def login(cls) -> Action:
        """Create a LOGIN action"""
        return cls(type="LOGIN", description="User login")

    @classmethod
    def logout(cls) -> Action:
        """Create a LOGOUT action"""
        return cls(type="LOGOUT", description="User logout")

    @classmethod
    def of(
        cls, type: str, description: Optional[str] = None, category: Optional[str] = None
    ) -> Action:
        """Create a custom action"""
        return cls(type=type, description=description, category=category)


class Resource(BaseModel):
    """Represents a resource being acted upon"""

    id: str
    type: str
    name: Optional[str] = None
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None

    @classmethod
    def of(cls, id: str, type: str, name: Optional[str] = None) -> Resource:
        """Create a custom resource"""
        return cls(id=id, type=type, name=name)

    @classmethod
    def document(cls, id: str, name: Optional[str] = None) -> Resource:
        """Create a document resource"""
        return cls(id=id, type="DOCUMENT", name=name)

    @classmethod
    def user(cls, id: str, name: Optional[str] = None) -> Resource:
        """Create a user resource"""
        return cls(id=id, type="USER", name=name)

    @classmethod
    def transaction(cls, id: str, name: Optional[str] = None) -> Resource:
        """Create a transaction resource"""
        return cls(id=id, type="TRANSACTION", name=name)

    def with_before(self, before: Dict[str, Any]) -> Resource:
        """Set the before state"""
        self.before = before
        return self

    def with_after(self, after: Dict[str, Any]) -> Resource:
        """Set the after state"""
        self.after = after
        return self


class EventMetadata(BaseModel):
    """Metadata for an audit event"""

    model_config = ConfigDict(populate_by_name=True)

    source: str
    tenant_id: str = Field(serialization_alias="tenantId")
    correlation_id: Optional[str] = Field(default=None, serialization_alias="correlationId")
    session_id: Optional[str] = Field(default=None, serialization_alias="sessionId")
    tags: Optional[Dict[str, str]] = None
    extra: Optional[Dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        source: str,
        tenant_id: str,
        correlation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> EventMetadata:
        """Create event metadata"""
        return cls(
            source=source,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            session_id=session_id,
            tags=tags,
        )


class Event(BaseModel):
    """Represents a complete audit event"""

    actor: Actor
    action: Action
    resource: Resource
    metadata: EventMetadata

    @classmethod
    def create(
        cls,
        actor: Actor,
        action: Action,
        resource: Resource,
        metadata: EventMetadata,
    ) -> Event:
        """Create an audit event"""
        return cls(actor=actor, action=action, resource=resource, metadata=metadata)


class EventResponse(BaseModel):
    """Response from logging an event"""

    id: str
    timestamp: Union[datetime, str]
    hash: str
    status: str


class BatchEventResponse(BaseModel):
    """Response from logging multiple events"""

    total: int
    succeeded: int
    failed: int
    events: List[EventResponse]
    errors: Optional[List[Dict[str, Any]]] = None


class SearchCriteria(BaseModel):
    """Criteria for searching events"""

    model_config = ConfigDict(populate_by_name=True)

    tenant_id: str = Field(serialization_alias="tenantId")
    actor_id: Optional[str] = Field(default=None, serialization_alias="actorId")
    actor_type: Optional[str] = Field(default=None, serialization_alias="actorType")
    action_type: Optional[str] = Field(default=None, serialization_alias="actionType")
    resource_id: Optional[str] = Field(default=None, serialization_alias="resourceId")
    resource_type: Optional[str] = Field(default=None, serialization_alias="resourceType")
    from_date: Optional[str] = Field(default=None, serialization_alias="fromDate")
    to_date: Optional[str] = Field(default=None, serialization_alias="toDate")
    query: Optional[str] = None
    page: int = 0
    size: int = 20


class SearchResult(BaseModel):
    """Result from searching events"""

    model_config = ConfigDict(populate_by_name=True)

    items: List[Dict[str, Any]]
    total_count: int = Field(alias="totalCount")
    page: int
    size: int
    total_pages: int = Field(alias="totalPages")
