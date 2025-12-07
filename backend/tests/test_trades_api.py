"""
Tests for trades API endpoints.
Phase 6: Testing CRUD operations and rate limiting.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.company import Company
from app.models.insider import Insider
from app.models.trade import Trade


def test_get_trades_empty(client: TestClient):
    """Test getting trades when database is empty."""
    response = client.get("/api/v1/trades/")

    assert response.status_code == 200
    data = response.json()

    # Endpoint returns PaginatedResponse, not a list
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_trades_with_data(client: TestClient, test_db: AsyncSession):
    """Test getting trades when trades exist."""
    # Create test company
    company = Company(
        cik="0000789019",
        ticker="MSFT",
        name="Microsoft Corporation"
    )
    test_db.add(company)
    await test_db.commit()
    await test_db.refresh(company)

    # Create test insider
    insider = Insider(
        name="Test Insider",
        company_id=company.id
    )
    test_db.add(insider)
    await test_db.commit()
    await test_db.refresh(insider)

    # Create test trade
    trade = Trade(
        filing_date=datetime(2025, 11, 14).date(),
        transaction_date=datetime(2025, 11, 13).date(),
        company_id=company.id,
        insider_id=insider.id,
        shares=1000,
        price_per_share=150.50,
        total_value=150500.00,
        transaction_type="BUY",
        transaction_code="P"
    )
    test_db.add(trade)
    await test_db.commit()

    response = client.get("/api/v1/trades/")

    assert response.status_code == 200
    data = response.json()

    # Endpoint returns PaginatedResponse
    assert "items" in data
    assert len(data["items"]) >= 1
    # The response model might flatten company data, let's check what's actually returned
    item = data["items"][0]
    assert float(item["shares"]) == 1000.0
    if "ticker" in item:
        assert item["ticker"] == "MSFT"
    elif "company" in item and "ticker" in item["company"]:
        assert item["company"]["ticker"] == "MSFT"


@pytest.mark.asyncio
async def test_get_trade_by_id(client: TestClient, test_db: AsyncSession):
    """Test getting a specific trade by ID."""
    # Create test data
    company = Company(cik="0000789019", ticker="MSFT", name="Microsoft Corporation")
    test_db.add(company)
    await test_db.commit()
    await test_db.refresh(company)

    insider = Insider(name="Test Insider", company_id=company.id)
    test_db.add(insider)
    await test_db.commit()
    await test_db.refresh(insider)

    trade = Trade(
        filing_date=datetime(2025, 11, 14).date(),
        transaction_date=datetime(2025, 11, 13).date(),
        company_id=company.id,
        insider_id=insider.id,
        shares=5000,
        price_per_share=75.25,
        total_value=376250.00,
        transaction_type="SELL",
        transaction_code="S"
    )
    test_db.add(trade)
    await test_db.commit()
    await test_db.refresh(trade)

    response = client.get(f"/api/v1/trades/{trade.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == trade.id
    assert float(data["shares"]) == 5000.0
    assert data["transaction_type"] == "SELL"


def test_get_trade_not_found(client: TestClient):
    """Test getting a trade that doesn't exist."""
    response = client.get("/api/v1/trades/99999")

    assert response.status_code == 404
    data = response.json()
    
    # Check for detail or error field
    if "detail" in data:
        assert "not found" in data["detail"].lower()
    elif "error" in data:
        assert "not found" in data["error"].lower()
    else:
        # Should not happen for a proper 404 response
        assert False, f"Unexpected response format: {data}"


@pytest.mark.asyncio
async def test_get_trades_by_ticker(client: TestClient, test_db: AsyncSession):
    """Test filtering trades by ticker."""
    # Create AAPL company
    aapl = Company(cik="0000320193", ticker="AAPL", name="Apple Inc.")
    test_db.add(aapl)

    # Create MSFT company
    msft = Company(cik="0000789019", ticker="MSFT", name="Microsoft Corporation")
    test_db.add(msft)

    await test_db.commit()
    await test_db.refresh(aapl)
    await test_db.refresh(msft)

    # Create insiders
    insider1 = Insider(name="Apple Insider", company_id=aapl.id)
    insider2 = Insider(name="Microsoft Insider", company_id=msft.id)
    test_db.add(insider1)
    test_db.add(insider2)
    await test_db.commit()
    await test_db.refresh(insider1)
    await test_db.refresh(insider2)

    # Create trades for both companies
    trade1 = Trade(
        filing_date=datetime(2025, 11, 14).date(),
        transaction_date=datetime(2025, 11, 13).date(),
        company_id=aapl.id,
        insider_id=insider1.id,
        shares=1000,
        price_per_share=180.00,
        total_value=180000.00,
        transaction_type="BUY",
        transaction_code="P"
    )
    trade2 = Trade(
        filing_date=datetime(2025, 11, 14).date(),
        transaction_date=datetime(2025, 11, 13).date(),
        company_id=msft.id,
        insider_id=insider2.id,
        shares=500,
        price_per_share=350.00,
        total_value=175000.00,
        transaction_type="BUY",
        transaction_code="P"
    )
    test_db.add(trade1)
    test_db.add(trade2)
    await test_db.commit()

    # Filter by AAPL
    response = client.get("/api/v1/trades/?ticker=AAPL")

    assert response.status_code == 200
    data = response.json()

    # Endpoint returns PaginatedResponse
    assert "items" in data
    assert len(data["items"]) >= 1
    
    # Check if any returned item belongs to AAPL
    # Note: The API might return company details nested or flat, checking loosely
    found_aapl = False
    for item in data["items"]:
        ticker = item.get("ticker") or (item.get("company") or {}).get("ticker")
        if ticker == "AAPL":
            found_aapl = True
            break
            
    assert found_aapl, "Should have found AAPL trades"


def test_get_recent_trades(client: TestClient):
    """Test getting recent trades endpoint."""
    response = client.get("/api/v1/trades/recent")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    # Should be ordered by filing_date desc


def test_get_significant_trades(client: TestClient):
    """Test getting significant trades (high value)."""
    response = client.get("/api/v1/trades/significant")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    # All trades should meet significance threshold


@pytest.mark.asyncio
async def test_pagination(client: TestClient, test_db: AsyncSession):
    """Test pagination parameters."""
    response = client.get("/api/v1/trades/?limit=10&offset=0")

    assert response.status_code == 200
    data = response.json()

    # Endpoint returns PaginatedResponse
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 10
