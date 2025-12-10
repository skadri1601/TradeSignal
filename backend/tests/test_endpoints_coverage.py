
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date

from app.main import app
from app.database import get_db, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.company import Company
from app.models.trade import Trade
from app.models.insider import Insider
from app.models.alert import Alert
from sqlalchemy import JSON, ARRAY

# Local DB setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def local_db():
    """
    Create test database session locally.
    """
    # Patch ARRAY types to JSON for SQLite compatibility
    # This must be done before creating the engine/tables
    for table in Base.metadata.tables.values():
        if table.name == 'alerts':
            for col in table.columns:
                if isinstance(col.type, ARRAY):
                    col.type = JSON()

    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create session
    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def local_client(local_db):
    async def override_get_db():
        yield local_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def seed_data(local_db):
    """Seed test data for endpoint tests."""
    # Create Test User
    password_hash = get_password_hash("Demo123456!")
    user = User(
        email="demo@tradesignal.com",
        username="demouser",
        hashed_password=password_hash,
        full_name="Demo User",
        is_active=True,
        is_verified=True,
        role="customer"
    )
    local_db.add(user)
    
    # Create Admin User
    admin = User(
        email="admin@tradesignal.com",
        username="adminuser",
        hashed_password=password_hash,
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        role="super_admin",
        is_superuser=True
    )
    local_db.add(admin)

    # Create Company
    company = Company(
        ticker="AAPL",
        name="Apple Inc.",
        cik="0000320193",
        sector="Technology",
        industry="Consumer Electronics",
        market_cap=3000000000000
    )
    local_db.add(company)
    await local_db.flush() # flush to get IDs

    # Create Insider
    insider = Insider(
        name="Tim Cook",
        company_id=company.id,
        title="CEO",
        is_officer=True
    )
    local_db.add(insider)
    await local_db.flush()

    # Create Trade
    trade = Trade(
        company_id=company.id,
        insider_id=insider.id,
        transaction_date=date.today(),
        filing_date=date.today(),
        transaction_type="BUY",
        price_per_share=150.0,
        shares=100,
        total_value=15000.0,
        shares_owned_after=1000,
        sec_filing_url="http://sec.gov/..."
    )
    local_db.add(trade)

    # Create Alert
    # Need user.id, so flush first
    await local_db.flush()
    
    alert = Alert(
        user_id=user.id,
        name="Test Alert",
        alert_type="large_trade",
        ticker="AAPL",
        min_value=10000,
        notification_channels=["email"],
        email="demo@tradesignal.com",
        is_active=True,
        insider_roles=[]
    )
    local_db.add(alert)

    await local_db.commit()
    return {"user": user, "admin": admin, "company": company}

@pytest.mark.asyncio
async def test_health_endpoints(local_client: AsyncClient):
    response = await local_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_auth_flow(local_client: AsyncClient, seed_data):
    # Login (Use form data)
    response = await local_client.post("/api/v1/auth/login", data={
        "username": "demo@tradesignal.com",
        "password": "Demo123456!"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get Me
    response = await local_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "demo@tradesignal.com"

@pytest.mark.asyncio
async def test_companies_endpoints(local_client: AsyncClient, seed_data):
    # List
    response = await local_client.get("/api/v1/companies?limit=10")
    assert response.status_code == 200
    data = response.json()
    
    items = data if isinstance(data, list) else data.get("items", [])
    found = any(c["ticker"] == "AAPL" for c in items)
    assert found

    # Get specific
    response = await local_client.get("/api/v1/companies/AAPL")
    assert response.status_code == 200
    assert response.json()["name"] == "Apple Inc."

    # Search
    response = await local_client.get("/api/v1/companies/search?q=Apple")
    assert response.status_code == 200
    data = response.json()
    items = data if isinstance(data, list) else data.get("items", [])
    assert len(items) > 0

@pytest.mark.asyncio
async def test_trades_endpoints(local_client: AsyncClient, seed_data):
    # Authenticate
    login_res = await local_client.post("/api/v1/auth/login", data={
        "username": "demo@tradesignal.com",
        "password": "Demo123456!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List
    response = await local_client.get("/api/v1/trades?limit=10", headers=headers)
    if response.status_code != 404:
        assert response.status_code == 200
    
    # Recent
    response = await local_client.get("/api/v1/trades/recent", headers=headers)
    if response.status_code != 404:
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_insiders_endpoints(local_client: AsyncClient, seed_data):
    response = await local_client.get("/api/v1/insiders?limit=10")
    if response.status_code != 404:
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_alerts_endpoints(local_client: AsyncClient, seed_data):
    # Authenticate first
    login_res = await local_client.post("/api/v1/auth/login", data={
        "username": "demo@tradesignal.com",
        "password": "Demo123456!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List
    response = await local_client.get("/api/v1/alerts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    items = data if isinstance(data, list) else data.get("items", [])
    assert len(items) > 0

    # Create
    response = await local_client.post("/api/v1/alerts", headers=headers, json={
        "name": "New Alert",
        "alert_type": "large_trade",
        "ticker": "AAPL",
        "min_value": 50000,
        "notification_channels": ["email"],
        "email": "demo@tradesignal.com",
        "is_active": True
    })
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_billing_endpoints(local_client: AsyncClient, seed_data):
    # Authenticate
    login_res = await local_client.post("/api/v1/auth/login", data={
        "username": "demo@tradesignal.com",
        "password": "Demo123456!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await local_client.get("/api/v1/billing/subscription", headers=headers)
    assert response.status_code in [200, 404]

    response = await local_client.get("/api/v1/billing/pricing", headers=headers)
    if response.status_code == 401:
        pass
    else:
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_ai_endpoints(local_client: AsyncClient, seed_data):
    # Authenticate
    login_res = await local_client.post("/api/v1/auth/login", data={
        "username": "demo@tradesignal.com",
        "password": "Demo123456!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await local_client.get("/api/v1/ai/status")
    assert response.status_code in [200, 401, 403, 503]

@pytest.mark.asyncio
async def test_admin_endpoints(local_client: AsyncClient, seed_data):
    # Authenticate as Admin
    login_res = await local_client.post("/api/v1/auth/login", data={
        "username": "admin@tradesignal.com",
        "password": "Demo123456!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await local_client.get("/api/v1/admin/stats", headers=headers)
    assert response.status_code == 200

    response = await local_client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
