"""
Interactive Brokers Client

Implementation of BaseBrokerClient for Interactive Brokers.
Uses the ib_insync library for API interactions.
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime
import asyncio

from ib_insync import IB, MarketOrder, LimitOrder, StopOrder, StopLimitOrder, Stock, util

from .base import BaseBrokerClient

logger = logging.getLogger(__name__)


class InteractiveBrokersClient(BaseBrokerClient):
    """Interactive Brokers API client."""

    def __init__(self, access_token: str):
        """
        Initialize Interactive Brokers client.

        Args:
            access_token: OAuth access token (already decrypted)

        Note: IB uses a different authentication model. The access_token
        is used to authenticate API gateway connections.
        """
        super().__init__(access_token)
        self.ib = IB()
        self.connected = False

    async def _ensure_connected(self):
        """Ensure IB connection is established."""
        if not self.connected:
            try:
                # Connect to IB Gateway (assumes gateway is running)
                # In production, you'd use the access_token to authenticate
                await self.ib.connectAsync('127.0.0.1', 4001, clientId=1)
                self.connected = True
            except Exception as e:
                logger.error(f"IB connection error: {e}")
                raise

    # ========================================================================
    # ACCOUNT INFORMATION
    # ========================================================================

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            await self._ensure_connected()

            # Get account summary
            account_values = self.ib.accountSummary()

            # Parse account values
            balance = Decimal(0)
            buying_power = Decimal(0)
            portfolio_value = Decimal(0)

            for av in account_values:
                if av.tag == "TotalCashValue":
                    balance = Decimal(str(av.value))
                elif av.tag == "BuyingPower":
                    buying_power = Decimal(str(av.value))
                elif av.tag == "NetLiquidation":
                    portfolio_value = Decimal(str(av.value))

            # Get positions count
            positions = self.ib.positions()

            # Get account number
            accounts = self.ib.managedAccounts()
            account_number = accounts[0] if accounts else "UNKNOWN"

            return {
                "account_number": account_number,
                "balance": balance,
                "buying_power": buying_power,
                "portfolio_value": portfolio_value,
                "positions_count": len(positions),
            }
        except Exception as e:
            logger.error(f"IB get_account_info error: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions."""
        try:
            await self._ensure_connected()

            positions = self.ib.positions()
            result = []

            for pos in positions:
                # Get current price
                contract = pos.contract
                ticker = self.ib.reqTickers(contract)[0]

                qty = Decimal(str(pos.position))
                avg_cost = Decimal(str(pos.avgCost))
                current_price = Decimal(str(ticker.marketPrice()))

                market_value = qty * current_price
                cost_basis = qty * avg_cost
                unrealized_pl = market_value - cost_basis
                unrealized_pl_pct = (unrealized_pl / cost_basis * 100) if cost_basis > 0 else Decimal(0)

                result.append({
                    "ticker": contract.symbol,
                    "quantity": qty,
                    "market_value": market_value,
                    "cost_basis": cost_basis,
                    "unrealized_pl": unrealized_pl,
                    "unrealized_pl_pct": unrealized_pl_pct,
                    "current_price": current_price,
                })

            return result
        except Exception as e:
            logger.error(f"IB get_positions error: {e}")
            raise

    # ========================================================================
    # ORDER MANAGEMENT
    # ========================================================================

    async def place_order(
        self,
        ticker: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        time_in_force: str = "day",
    ) -> Dict[str, Any]:
        """Place an order."""
        try:
            await self._ensure_connected()

            # Create contract
            contract = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)

            # Determine action
            action = "BUY" if side.lower() == "buy" else "SELL"
            qty = float(quantity)

            # Create order based on type
            if order_type.lower() == "market":
                order = MarketOrder(action, qty)
            elif order_type.lower() == "limit":
                if not limit_price:
                    raise ValueError("limit_price required for limit orders")
                order = LimitOrder(action, qty, float(limit_price))
            elif order_type.lower() == "stop":
                if not stop_price:
                    raise ValueError("stop_price required for stop orders")
                order = StopOrder(action, qty, float(stop_price))
            elif order_type.lower() == "stop_limit":
                if not limit_price or not stop_price:
                    raise ValueError("limit_price and stop_price required for stop_limit orders")
                order = StopLimitOrder(action, qty, float(limit_price), float(stop_price))
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            # Set time in force
            if time_in_force.lower() == "gtc":
                order.tif = "GTC"
            elif time_in_force.lower() == "ioc":
                order.tif = "IOC"
            elif time_in_force.lower() == "fok":
                order.tif = "FOK"
            else:
                order.tif = "DAY"

            # Place order
            trade = self.ib.placeOrder(contract, order)

            # Wait for order to be submitted
            while not trade.isDone():
                await asyncio.sleep(0.1)
                if trade.orderStatus.status in ['Submitted', 'PreSubmitted']:
                    break

            filled_qty = Decimal(str(trade.orderStatus.filled))
            avg_fill_price = Decimal(str(trade.orderStatus.avgFillPrice)) if trade.orderStatus.avgFillPrice > 0 else None

            return {
                "broker_order_id": str(trade.order.orderId),
                "status": self._map_order_status(trade.orderStatus.status),
                "filled_quantity": filled_qty,
                "filled_price": avg_fill_price,
                "created_at": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"IB place_order error: {e}")
            raise

    async def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """Get order status."""
        try:
            await self._ensure_connected()

            # Get all trades and find matching order
            trades = self.ib.trades()

            for trade in trades:
                if str(trade.order.orderId) == broker_order_id:
                    filled_qty = Decimal(str(trade.orderStatus.filled))
                    avg_fill_price = Decimal(str(trade.orderStatus.avgFillPrice)) if trade.orderStatus.avgFillPrice > 0 else None

                    return {
                        "broker_order_id": broker_order_id,
                        "ticker": trade.contract.symbol,
                        "side": trade.order.action.lower(),
                        "quantity": Decimal(str(trade.order.totalQuantity)),
                        "filled_quantity": filled_qty,
                        "filled_price": avg_fill_price,
                        "status": self._map_order_status(trade.orderStatus.status),
                        "created_at": datetime.utcnow(),  # IB doesn't provide creation time easily
                        "updated_at": datetime.utcnow(),
                    }

            raise ValueError(f"Order {broker_order_id} not found")
        except Exception as e:
            logger.error(f"IB get_order_status error: {e}")
            raise

    async def cancel_order(self, broker_order_id: str) -> bool:
        """Cancel an order."""
        try:
            await self._ensure_connected()

            # Find order
            trades = self.ib.trades()
            for trade in trades:
                if str(trade.order.orderId) == broker_order_id:
                    self.ib.cancelOrder(trade.order)
                    return True

            return False
        except Exception as e:
            logger.error(f"IB cancel_order error: {e}")
            return False

    async def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders."""
        try:
            await self._ensure_connected()

            trades = self.ib.trades()
            result = []

            for trade in trades[-limit:]:
                filled_qty = Decimal(str(trade.orderStatus.filled))
                avg_fill_price = Decimal(str(trade.orderStatus.avgFillPrice)) if trade.orderStatus.avgFillPrice > 0 else None

                result.append({
                    "broker_order_id": str(trade.order.orderId),
                    "ticker": trade.contract.symbol,
                    "side": trade.order.action.lower(),
                    "quantity": Decimal(str(trade.order.totalQuantity)),
                    "filled_quantity": filled_qty,
                    "filled_price": avg_fill_price,
                    "status": self._map_order_status(trade.orderStatus.status),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                })

            return result
        except Exception as e:
            logger.error(f"IB get_recent_orders error: {e}")
            raise

    # ========================================================================
    # MARKET DATA
    # ========================================================================

    async def get_current_price(self, ticker: str) -> Decimal:
        """Get current market price for a ticker."""
        try:
            await self._ensure_connected()

            contract = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)

            ticker_obj = self.ib.reqTickers(contract)[0]
            price = ticker_obj.marketPrice()

            if price > 0:
                return Decimal(str(price))
            else:
                # Fallback to last price
                return Decimal(str(ticker_obj.last))
        except Exception as e:
            logger.error(f"IB get_current_price error: {e}")
            raise

    # ========================================================================
    # VALIDATION
    # ========================================================================

    async def validate_connection(self) -> bool:
        """Validate connection."""
        try:
            await self._ensure_connected()
            return self.ib.isConnected()
        except Exception as e:
            logger.error(f"IB validate_connection error: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _map_order_status(self, ib_status: str) -> str:
        """Map IB order status to our standard status."""
        status_map = {
            "PendingSubmit": "pending",
            "PendingCancel": "pending",
            "PreSubmitted": "pending",
            "Submitted": "pending",
            "ApiPending": "pending",
            "Cancelled": "cancelled",
            "Filled": "filled",
            "Inactive": "cancelled",
            "ApiCancelled": "cancelled",
        }
        return status_map.get(ib_status, "pending")

    async def disconnect(self):
        """Disconnect from IB."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
