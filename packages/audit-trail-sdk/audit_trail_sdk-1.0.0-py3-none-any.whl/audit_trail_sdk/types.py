"""Type definitions for Audit Trail SDK"""

from enum import Enum


class ActorType(str, Enum):
    """Types of actors that can perform actions"""

    USER = "USER"
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"


class ActionType(str, Enum):
    """Common action types"""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
