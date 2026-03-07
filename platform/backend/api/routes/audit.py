"""Audit log API endpoints."""

import io
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.audit import AuditLogEntry
from api.schemas.common import APIResponse, PaginatedResponse
from core.database import get_db
from middleware.auth import get_current_user
from models.audit_log import AuditLog
from models.user import User

router = APIRouter()


@router.get("/logs", response_model=APIResponse[PaginatedResponse[AuditLogEntry]])
async def get_audit_logs(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    userId: Optional[str] = Query(None, alias="userId"),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None, alias="startDate"),
    endDate: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100, alias="pageSize"),
) -> APIResponse[PaginatedResponse[AuditLogEntry]]:
    """Get paginated audit logs with optional filters."""
    q = (
        select(AuditLog, User.username)
        .outerjoin(User, AuditLog.user_id == User.id)
        .order_by(AuditLog.timestamp.desc())
    )
    if userId:
        q = q.where(AuditLog.user_id == int(userId) if userId.isdigit() else AuditLog.user_id.is_(None))
    if action:
        q = q.where(AuditLog.action == action)
    if resource:
        q = q.where(AuditLog.resource == resource)
    if startDate:
        q = q.where(func.date(AuditLog.timestamp) >= startDate)
    if endDate:
        q = q.where(func.date(AuditLog.timestamp) <= endDate)

    count_q = select(func.count(AuditLog.id)).select_from(AuditLog)
    if userId:
        count_q = count_q.where(AuditLog.user_id == int(userId) if userId.isdigit() else AuditLog.user_id.is_(None))
    if action:
        count_q = count_q.where(AuditLog.action == action)
    if resource:
        count_q = count_q.where(AuditLog.resource == resource)
    if startDate:
        count_q = count_q.where(func.date(AuditLog.timestamp) >= startDate)
    if endDate:
        count_q = count_q.where(func.date(AuditLog.timestamp) <= endDate)
    total = (await db.execute(count_q)).scalar() or 0

    q = q.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(q)
    rows = result.all()

    items = [
        AuditLogEntry(
            id=str(row[0].id),
            userId=str(row[0].user_id) if row[0].user_id else None,
            username=row[1] or "",
            action=row[0].action,
            resource=row[0].resource,
            details=row[0].details,
            ipAddress=row[0].ip,
            timestamp=row[0].timestamp.isoformat() if row[0].timestamp else "",
            success=True,
        )
        for row in rows
    ]

    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=pageSize,
            total_pages=(total + pageSize - 1) // pageSize if pageSize else 0,
        )
    )


@router.get("/export")
async def export_audit_logs(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    userId: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
):
    """Export audit logs as CSV (Excel-compatible)."""
    q = (
        select(AuditLog, User.username)
        .outerjoin(User, AuditLog.user_id == User.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(10000)
    )
    if userId:
        q = q.where(AuditLog.user_id == int(userId) if userId.isdigit() else AuditLog.user_id.is_(None))
    if action:
        q = q.where(AuditLog.action == action)
    if resource:
        q = q.where(AuditLog.resource == resource)
    if startDate:
        q = q.where(func.date(AuditLog.timestamp) >= startDate)
    if endDate:
        q = q.where(func.date(AuditLog.timestamp) <= endDate)

    result = await db.execute(q)
    rows = result.all()

    buf = io.StringIO()
    buf.write("时间,用户,操作,资源,IP,详情,状态\n")
    for row in rows:
        ts = row[0].timestamp.strftime("%Y-%m-%d %H:%M:%S") if row[0].timestamp else ""
        username = (row[1] or "").replace(",", " ")
        action_val = (row[0].action or "").replace(",", " ")
        resource_val = (row[0].resource or "").replace(",", " ")
        ip_val = (row[0].ip or "").replace(",", " ")
        details_val = (row[0].details or "").replace(",", " ").replace("\n", " ")
        buf.write(f'"{ts}","{username}","{action_val}","{resource_val}","{ip_val}","{details_val}","成功"\n')

    output = io.BytesIO(buf.getvalue().encode("utf-8-sig"))
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"},
    )
