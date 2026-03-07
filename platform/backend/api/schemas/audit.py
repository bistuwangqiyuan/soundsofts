"""Audit log schemas."""

from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    """Audit log entry for API response."""

    id: str
    userId: str | None = None
    username: str = ""
    action: str
    resource: str
    details: str | None = None
    ipAddress: str | None = None
    timestamp: str
    success: bool = True
