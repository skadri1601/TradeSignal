"""
Pydantic schemas for TradeSignal API.

Import all schemas here for easy access.
"""

from app.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyRead,
    CompanyWithStats,
    CompanySearch,
)
from app.schemas.insider import (
    InsiderBase,
    InsiderCreate,
    InsiderUpdate,
    InsiderRead,
    InsiderWithCompany,
    InsiderWithStats,
)
from app.schemas.trade import (
    TradeBase,
    TradeCreate,
    TradeUpdate,
    TradeRead,
    TradeWithDetails,
    TradeFilter,
    TradeStats,
)
from app.schemas.common import (
    PaginationParams,
    SortParams,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)

__all__ = [
    # Company schemas
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyRead",
    "CompanyWithStats",
    "CompanySearch",
    # Insider schemas
    "InsiderBase",
    "InsiderCreate",
    "InsiderUpdate",
    "InsiderRead",
    "InsiderWithCompany",
    "InsiderWithStats",
    # Trade schemas
    "TradeBase",
    "TradeCreate",
    "TradeUpdate",
    "TradeRead",
    "TradeWithDetails",
    "TradeFilter",
    "TradeStats",
    # Common schemas
    "PaginationParams",
    "SortParams",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
]
