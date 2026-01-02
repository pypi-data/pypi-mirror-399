"""Custom exceptions for Audit Trail SDK"""

from typing import Any, List, Optional


class AuditTrailError(Exception):
    """Base exception for Audit Trail SDK"""

    pass


class AuditTrailConnectionError(AuditTrailError):
    """Raised when connection to server fails"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause


class AuditTrailApiError(AuditTrailError):
    """Raised when API returns an error"""

    def __init__(self, message: str, status_code: int, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuditTrailValidationError(AuditTrailError):
    """Raised when validation fails"""

    def __init__(self, message: str, violations: Optional[List[str]] = None):
        super().__init__(message)
        self.violations = violations or []
