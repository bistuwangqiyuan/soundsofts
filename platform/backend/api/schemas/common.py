"""Standard response schemas for API consistency."""

from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    success: bool = True
    data: T | None = None
    message: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    detail: str = ""
    code: str | None = None
