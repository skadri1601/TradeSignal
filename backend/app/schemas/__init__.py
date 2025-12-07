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
from app.schemas.congressperson import (
    CongresspersonBase,
    CongresspersonCreate,
    CongresspersonUpdate,
    CongresspersonRead,
    CongresspersonFilter,
)
from app.schemas.congressional_trade import (
    CongressionalTradeBase,
    CongressionalTradeCreate,
    CongressionalTradeUpdate,
    CongressionalTradeRead,
    CongressionalTradeWithDetails,
    CongressionalTradeFilter,
    CongressionalTradeStats,
)
from app.schemas.common import (
    PaginationParams,
    SortParams,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)
from app.schemas.job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobApplicationBase,
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationListResponse,
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
    # Congressperson schemas
    "CongresspersonBase",
    "CongresspersonCreate",
    "CongresspersonUpdate",
    "CongresspersonRead",
    "CongresspersonFilter",
    # Congressional Trade schemas
    "CongressionalTradeBase",
    "CongressionalTradeCreate",
    "CongressionalTradeUpdate",
    "CongressionalTradeRead",
    "CongressionalTradeWithDetails",
    "CongressionalTradeFilter",
    "CongressionalTradeStats",
    # Common schemas
    "PaginationParams",
    "SortParams",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    # Job schemas
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "JobApplicationBase",
    "JobApplicationCreate",
    "JobApplicationResponse",
    "JobApplicationStatusUpdate",
    "JobApplicationListResponse",
]
