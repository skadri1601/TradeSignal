"""
Company model for TradeSignal.

Represents publicly traded companies tracked by the platform.
"""

from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, BigInteger, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.insider import Insider
    from app.models.trade import Trade


class Company(Base):
    """
    Company model representing publicly traded companies.

    Attributes:
        id: Primary key
        ticker: Stock ticker symbol (e.g., AAPL, TSLA)
        name: Company name
        cik: SEC Central Index Key (unique identifier)
        sector: Business sector (Technology, Finance, etc.)
        industry: Specific industry
        market_cap: Market capitalization in USD
        description: Company description
        website: Company website URL
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "companies"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Core Fields
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cik: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)

    # Classification
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Financial Data
    market_cap: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Additional Info
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    insiders: Mapped[List["Insider"]] = relationship(
        "Insider",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    trades: Mapped[List["Trade"]] = relationship(
        "Trade",
        back_populates="company",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Company."""
        return f"<Company(id={self.id}, ticker={self.ticker}, name={self.name})>"

    @property
    def ticker_upper(self) -> str:
        """Return ticker in uppercase."""
        return self.ticker.upper() if self.ticker else ""

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "ticker": self.ticker,
            "name": self.name,
            "cik": self.cik,
            "sector": self.sector,
            "industry": self.industry,
            "market_cap": self.market_cap,
            "description": self.description,
            "website": self.website,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
