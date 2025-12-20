"""
Alpaca Broker Client

Implementation of BaseBrokerClient for Alpaca Markets.
Uses the alpaca-py library for API interactions.
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

from .base import BaseBrokerClient

logger = logging.getLogger(__name__)


class AlpacaClient(BaseBrokerClient):
    """Alpaca broker API client."""

    def __init__(self, access_token: str):
        """
        Initialize Alpaca client.

        Args:
            access_token: OAuth access token (already decrypted)
        """
        super().__init__(access_token)
        self.trading_client = TradingClient(api_key=access_token, secret_key="", paper=False)
        self.data_client = StockHistoricalDataClient(api_key=access_token, secret_key="")

    # ========================================================================
    # ACCOUNT INFORMATION
    # ========================================================================

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            account = self.trading_client.get_account()
            return {
                "account_number": account.account_number,
                "balance": Decimal(str(account.cash)),
                "buying_power": Decimal(str(account.buying_power)),
                "portfolio_value": Decimal(str(account.portfolio_value)),
                "positions_count": len(self.trading_client.get_all_positions()),
            }
        except Exception as e:
            logger.error(f"Alpaca get_account_info error: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions."""
        try:
            positions = self.trading_client.get_all_positions()
            result = []
            for pos in positions:
                result.append({
                    "ticker": pos.symbol,
                    "quantity": Decimal(str(pos.qty)),
                    "market_value": Decimal(str(pos.market_value)),
                    "cost_basis": Decimal(str(pos.cost_basis)),
                    "unrealized_pl": Decimal(str(pos.unrealized_pl)),
                    "unrealized_pl_pct": Decimal(str(pos.unrealized_plpc)) * 100,
                    "current_price": Decimal(str(pos.current_price)),
                })
            return result
        except Exception as e:
            logger.error(f"Alpaca get_positions error: {e}")
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
            # Map side
            alpaca_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL

            # Map time in force
            tif_map = {
                "day": TimeInForce.DAY,
                "gtc": TimeInForce.GTC,
                "ioc": TimeInForce.IOC,
                "fok": TimeInForce.FOK,
            }
            alpaca_tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)

            # Create order request based on type
            order_request = self._create_order_request(
                ticker, quantity, alpaca_side, alpaca_tif, order_type, limit_price, stop_price
            )

            # Submit order
            order = self.trading_client.submit_order(order_request)

            return {
                "broker_order_id": order.id,
                "status": order.status.value,
                "filled_quantity": Decimal(str(order.filled_qty)) if order.filled_qty else Decimal(0),
                "filled_price": Decimal(str(order.filled_avg_price)) if order.filled_avg_price else None,
                "created_at": order.created_at,
            }
        except Exception as e:
            logger.error(f"Alpaca place_order error: {e}")
            raise

    async def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """Get order status."""
        try:
            order = self.trading_client.get_order_by_id(broker_order_id)
            return {
                "broker_order_id": order.id,
                "ticker": order.symbol,
                "side": order.side.value,
                "quantity": Decimal(str(order.qty)),
                "filled_quantity": Decimal(str(order.filled_qty)) if order.filled_qty else Decimal(0),
                "filled_price": Decimal(str(order.filled_avg_price)) if order.filled_avg_price else None,
                "status": self._map_order_status(order.status.value),
                "created_at": order.created_at,
                "updated_at": order.updated_at,
            }
        except Exception as e:
            logger.error(f"Alpaca get_order_status error: {e}")
            raise

    async def cancel_order(self, broker_order_id: str) -> bool:
        """Cancel an order."""
        try:
            self.trading_client.cancel_order_by_id(broker_order_id)
            return True
        except Exception as e:
            logger.error(f"Alpaca cancel_order error: {e}")
            return False

    async def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders."""
        try:
            orders = self.trading_client.get_orders(limit=limit)
            result = []
            for order in orders:
                result.append({
                    "broker_order_id": order.id,
                    "ticker": order.symbol,
                    "side": order.side.value,
                    "quantity": Decimal(str(order.qty)),
                    "filled_quantity": Decimal(str(order.filled_qty)) if order.filled_qty else Decimal(0),
                    "filled_price": Decimal(str(order.filled_avg_price)) if order.filled_avg_price else None,
                    "status": self._map_order_status(order.status.value),
                    "created_at": order.created_at,
                    "updated_at": order.updated_at,
                })
            return result
        except Exception as e:
            logger.error(f"Alpaca get_recent_orders error: {e}")
            raise

    # ========================================================================
    # MARKET DATA
    # ========================================================================

    async def get_current_price(self, ticker: str) -> Decimal:
        """Get current market price for a ticker."""
        try:
            request_params = StockLatestQuoteRequest(symbol_or_symbols=ticker)
            quote = self.data_client.get_stock_latest_quote(request_params)

            # The result is a dict with ticker as key
            if ticker in quote:
                latest_quote = quote[ticker]
                # Use mid-price between bid and ask
                bid = Decimal(str(latest_quote.bid_price))
                ask = Decimal(str(latest_quote.ask_price))
                return (bid + ask) / 2
            else:
                raise ValueError(f"No quote data for {ticker}")
        except Exception as e:
            logger.error(f"Alpaca get_current_price error: {e}")
            raise

    # ========================================================================
    # VALIDATION
    # ========================================================================

    async def validate_connection(self) -> bool:
        """Validate connection."""
        try:
            self.trading_client.get_account()
            return True
        except Exception as e:
            logger.error(f"Alpaca validate_connection error: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _create_order_request(
        self,
        ticker: str,
        quantity: Decimal,
        alpaca_side: OrderSide,
        alpaca_tif: TimeInForce,
        order_type: str,
        limit_price: Optional[Decimal],
        stop_price: Optional[Decimal],
    ):
        """Create appropriate order request based on type."""
        qty = float(quantity)

        if order_type.lower() == "market":
            return MarketOrderRequest(
                symbol=ticker,
                qty=qty,
                side=alpaca_side,
                time_in_force=alpaca_tif,
            )
        elif order_type.lower() == "limit":
            if not limit_price:
                raise ValueError("limit_price required for limit orders")
            return LimitOrderRequest(
                symbol=ticker,
                qty=qty,
                side=alpaca_side,
                time_in_force=alpaca_tif,
                limit_price=float(limit_price),
            )
        elif order_type.lower() == "stop":
            if not stop_price:
                raise ValueError("stop_price required for stop orders")
            return StopOrderRequest(
                symbol=ticker,
                qty=qty,
                side=alpaca_side,
                time_in_force=alpaca_tif,
                stop_price=float(stop_price),
            )
        elif order_type.lower() == "stop_limit":
            if not limit_price or not stop_price:
                raise ValueError("limit_price and stop_price required for stop_limit orders")
            return StopLimitOrderRequest(
                symbol=ticker,
                qty=qty,
                side=alpaca_side,
                time_in_force=alpaca_tif,
                limit_price=float(limit_price),
                stop_price=float(stop_price),
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    def _map_order_status(self, alpaca_status: str) -> str:
        """Map Alpaca order status to our standard status."""
        status_map = {
            "accepted": "pending",
            "pending_new": "pending",
            "new": "pending",
            "partially_filled": "partial",
            "filled": "filled",
            "done_for_day": "cancelled",
            "canceled": "cancelled",
            "expired": "cancelled",
            "replaced": "cancelled",
            "pending_cancel": "pending",
            "pending_replace": "pending",
            "rejected": "failed",
            "suspended": "failed",
            "stopped": "failed",
        }
        return status_map.get(alpaca_status.lower(), "pending")
