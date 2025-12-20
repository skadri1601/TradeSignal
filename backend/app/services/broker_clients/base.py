"""
Base Broker Client

Abstract base class for all broker integrations.
Defines the interface that all broker clients must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime


class BaseBrokerClient(ABC):
    """Abstract base class for broker API clients."""

    def __init__(self, access_token: str):
        """
        Initialize broker client with access token.

        Args:
            access_token: OAuth access token (already decrypted)
        """
        self.access_token = access_token

    # ========================================================================
    # ACCOUNT INFORMATION
    # ========================================================================

    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information including balance, buying power, and portfolio value.

        Returns:
            Dictionary with keys:
            - account_number: str
            - balance: Decimal (cash balance)
            - buying_power: Decimal
            - portfolio_value: Decimal
            - positions_count: int
        """
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all current positions.

        Returns:
            List of dictionaries with keys:
            - ticker: str
            - quantity: Decimal
            - market_value: Decimal
            - cost_basis: Decimal
            - unrealized_pl: Decimal
            - unrealized_pl_pct: Decimal
            - current_price: Decimal
        """
        pass

    # ========================================================================
    # ORDER MANAGEMENT
    # ========================================================================

    @abstractmethod
    async def place_order(
        self,
        ticker: str,
        side: str,  # 'buy' or 'sell'
        quantity: Decimal,
        order_type: str = "market",  # 'market', 'limit', 'stop', 'stop_limit'
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        time_in_force: str = "day",  # 'day', 'gtc', 'ioc', 'fok'
    ) -> Dict[str, Any]:
        """
        Place an order.

        Args:
            ticker: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: Order type
            limit_price: Limit price for limit/stop_limit orders
            stop_price: Stop price for stop/stop_limit orders
            time_in_force: Time in force

        Returns:
            Dictionary with keys:
            - broker_order_id: str
            - status: str
            - filled_quantity: Decimal
            - filled_price: Decimal (if filled)
            - created_at: datetime
        """
        pass

    @abstractmethod
    async def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """
        Get order status.

        Args:
            broker_order_id: Broker's order ID

        Returns:
            Dictionary with keys:
            - broker_order_id: str
            - ticker: str
            - side: str
            - quantity: Decimal
            - filled_quantity: Decimal
            - filled_price: Decimal (if filled)
            - status: str ('pending', 'filled', 'partial', 'cancelled', 'failed')
            - created_at: datetime
            - updated_at: datetime
        """
        pass

    @abstractmethod
    async def cancel_order(self, broker_order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            broker_order_id: Broker's order ID

        Returns:
            True if cancelled successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent orders.

        Args:
            limit: Maximum number of orders to return

        Returns:
            List of order dictionaries (same format as get_order_status)
        """
        pass

    # ========================================================================
    # MARKET DATA
    # ========================================================================

    @abstractmethod
    async def get_current_price(self, ticker: str) -> Decimal:
        """
        Get current market price for a ticker.

        Args:
            ticker: Stock symbol

        Returns:
            Current price as Decimal
        """
        pass

    # ========================================================================
    # VALIDATION
    # ========================================================================

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate that the connection and credentials are working.

        Returns:
            True if connection is valid, False otherwise
        """
        pass
