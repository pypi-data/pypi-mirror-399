"""Audit Trail SDK for Python"""

from .client import AuditTrailClient, AuditTrailClientBuilder
from .exceptions import (
    AuditTrailApiError,
    AuditTrailConnectionError,
    AuditTrailError,
    AuditTrailValidationError,
)
from .models import (
    Action,
    Actor,
    BatchEventResponse,
    Event,
    EventMetadata,
    EventResponse,
    Resource,
    SearchCriteria,
    SearchResult,
)
from .types import ActionType, ActorType

__version__ = "1.0.0"

__all__ = [
    # Client
    "AuditTrailClient",
    "AuditTrailClientBuilder",
    # Models
    "Actor",
    "Action",
    "Resource",
    "EventMetadata",
    "Event",
    "EventResponse",
    "BatchEventResponse",
    "SearchCriteria",
    "SearchResult",
    # Types
    "ActorType",
    "ActionType",
    # Exceptions
    "AuditTrailError",
    "AuditTrailConnectionError",
    "AuditTrailApiError",
    "AuditTrailValidationError",
]
