"""Audit logging service for operation tracking."""

from typing import Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.audit_log import AuditLog


class AuditService:
    """Log audit events to database."""

    @classmethod
    async def log(
        cls,
        action: str,
        resource: str,
        user_id: Optional[int] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Log an audit event."""
        async with AsyncSessionLocal() as session:
            stmt = insert(AuditLog).values(
                user_id=user_id,
                action=action,
                resource=resource,
                ip=ip,
                user_agent=user_agent,
                details=details,
            )
            await session.execute(stmt)
            await session.commit()
