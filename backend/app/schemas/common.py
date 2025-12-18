"""
Common Pydantic schemas for pagination, sorting, and responses.
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field


# Generic type variable for response data
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def skip(self) -> int:
        """Calculate number of items to skip."""
        return (self.page - 1) * self.limit


class SortParams(BaseModel):
    """Schema for sorting parameters."""

    sort_by: str = Field("filing_date", description="Field to sort by")
    order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated API responses."""

    items: List[T] = Field(default_factory=list, description="List of items")
    total: int = Field(0, ge=0, description="Total number of items")
    page: int = Field(1, ge=1, description="Current page")
    limit: int = Field(20, ge=1, description="Items per page")
    pages: int = Field(1, ge=1, description="Total number of pages")
    has_next: bool = Field(False, description="Has next page")
    has_prev: bool = Field(False, description="Has previous page")

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, limit: int
    ) -> "PaginatedResponse[T]":
        """
        Create a paginated response.

        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            limit: Items per page

        Returns:
            PaginatedResponse instance
        """
        pages = (total + limit - 1) // limit if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


class SuccessResponse(BaseModel):
    """Schema for generic success response."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Optional response data")


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str = Field(..., description="Error message")
    status_code: int = Field(..., ge=400, le=599, description="HTTP status code")
    detail: Optional[Any] = Field(None, description="Additional error details")
