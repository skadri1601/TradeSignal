"""
Lobbying Activity model.

Tracks Senate lobbying disclosure reports and company-politician relationships.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LobbyingActivity(Base):
    """
    Store lobbying activity from Senate disclosure reports.

    Attributes:
        id: Primary key
        company_name: Company name
        ticker: Stock ticker symbol (if available)
        company_id: Foreign key to Company
        lobbyist_name: Name of lobbyist or firm
        issue: Lobbying issue/topic
        amount: Lobbying amount (if disclosed)
        filing_date: Date of disclosure filing
        period_start: Reporting period start
        period_end: Reporting period end
        created_at: When record was created
        updated_at: When record was last updated
    """

    __tablename__ = "lobbying_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ticker: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Lobbying details
    lobbyist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issue: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Filing information
    filing_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Source
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="senate")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_lobbying_activities_ticker_period", "ticker", "period_end"),
        Index("ix_lobbying_activities_company_period", "company_id", "period_end"),
    )

    def __repr__(self) -> str:
        return (
            f"<LobbyingActivity(company={self.company_name}, "
            f"lobbyist={self.lobbyist_name}, amount={self.amount})>"
        )


class CompanyPoliticianRelationship(Base):
    """
    Track company-politician relationships from lobbying and trading data.

    Correlates trades vs. lobbying activity.
    """

    __tablename__ = "company_politician_relationships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    congressperson_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("congresspeople.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationship metrics
    lobbying_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    trade_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trade_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)

    # Correlation score (0-100)
    correlation_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_company_politician_company", "company_id", "congressperson_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<CompanyPoliticianRelationship(company_id={self.company_id}, "
            f"congressperson_id={self.congressperson_id})>"
        )

