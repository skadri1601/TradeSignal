"""
TD Ameritrade Broker Client

Implementation of BaseBrokerClient for TD Ameritrade.
Uses the tda-api library for API interactions.
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime

from tda import auth, client
from tda.orders.equities import equity_buy_market, equity_sell_market, equity_buy_limit, equity_sell_limit

from .base import BaseBrokerClient

logger = logging.getLogger(__name__)


class TDAmeritradeClient(BaseBrokerClient):
    """TD Ameritrade broker API client."""

    def __init__(self, access_token: str):
        """
        Initialize TD Ameritrade client.

        Args:
            access_token: OAuth access token (already decrypted)
        """
        super().__init__(access_token)
        # Create client with manual token
        self.client = client.Client(api_key="", token_metadata={"access_token": access_token})

    # ========================================================================
    # ACCOUNT INFORMATION
    # ========================================================================

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            response = self.client.get_accounts()
            response.raise_for_status()
            accounts = response.json()

            # Use first account
            account = accounts[0]["securitiesAccount"]
            balances = account["currentBalances"]

            return {
                "account_number": account["accountId"],
                "balance": Decimal(str(balances.get("cashBalance", 0))),
                "buying_power": Decimal(str(balances.get("buyingPower", 0))),
                "portfolio_value": Decimal(str(balances.get("liquidationValue", 0))),
                "positions_count": len(account.get("positions", [])),
            }
        except Exception as e:
            logger.error(f"TD Ameritrade get_account_info error: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions."""
        try:
            response = self.client.get_accounts(fields=client.Client.Account.Fields.POSITIONS)
            response.raise_for_status()
            accounts = response.json()

            # Use first account
            account = accounts[0]["securitiesAccount"]
            positions = account.get("positions", [])

            result = []
            for pos in positions:
                instrument = pos.get("instrument", {})
                qty = Decimal(str(pos.get("longQuantity", 0)))
                market_value = Decimal(str(pos.get("marketValue", 0)))
                average_price = Decimal(str(pos.get("averagePrice", 0)))
                cost_basis = qty * average_price
                current_price = market_value / qty if qty > 0 else Decimal(0)
                unrealized_pl = market_value - cost_basis
                unrealized_pl_pct = (unrealized_pl / cost_basis * 100) if cost_basis > 0 else Decimal(0)

                result.append({
                    "ticker": instrument.get("symbol", ""),
                    "quantity": qty,
                    "market_value": market_value,
                    "cost_basis": cost_basis,
                    "unrealized_pl": unrealized_pl,
                    "unrealized_pl_pct": unrealized_pl_pct,
                    "current_price": current_price,
                })
            return result
        except Exception as e:
            logger.error(f"TD Ameritrade get_positions error: {e}")
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
            # Get account ID
            response = self.client.get_accounts()
            response.raise_for_status()
            account_id = response.json()[0]["securitiesAccount"]["accountId"]

            # Build order spec based on type and side
            qty = int(quantity)

            if order_type.lower() == "market":
                if side.lower() == "buy":
                    order_spec = equity_buy_market(ticker, qty)
                else:
                    order_spec = equity_sell_market(ticker, qty)
            elif order_type.lower() == "limit":
                if not limit_price:
                    raise ValueError("limit_price required for limit orders")
                if side.lower() == "buy":
                    order_spec = equity_buy_limit(ticker, qty, float(limit_price))
                else:
                    order_spec = equity_sell_limit(ticker, qty, float(limit_price))
            else:
                # For stop and stop_limit, we need to build manually
                raise ValueError(f"Order type {order_type} not yet implemented for TD Ameritrade")

            # Set time in force
            if time_in_force.lower() == "gtc":
                order_spec.set_duration(client.Order.Duration.GOOD_TILL_CANCEL)
            else:
                order_spec.set_duration(client.Order.Duration.DAY)

            # Place order
            response = self.client.place_order(account_id, order_spec.build())
            response.raise_for_status()

            # Extract order ID from Location header
            order_id = response.headers.get("Location", "").split("/")[-1]

            return {
                "broker_order_id": order_id,
                "status": "pending",
                "filled_quantity": Decimal(0),
                "filled_price": None,
                "created_at": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"TD Ameritrade place_order error: {e}")
            raise

    async def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """Get order status."""
        try:
            # Get account ID
            response = self.client.get_accounts()
            response.raise_for_status()
            account_id = response.json()[0]["securitiesAccount"]["accountId"]

            # Get order
            response = self.client.get_order(broker_order_id, account_id)
            response.raise_for_status()
            order = response.json()

            # Extract order details
            leg = order["orderLegCollection"][0]
            instrument = leg["instrument"]

            filled_qty = Decimal(str(order.get("filledQuantity", 0)))
            total_qty = Decimal(str(order.get("quantity", 0)))

            return {
                "broker_order_id": str(order["orderId"]),
                "ticker": instrument.get("symbol", ""),
                "side": leg["instruction"].lower().replace("_", " "),
                "quantity": total_qty,
                "filled_quantity": filled_qty,
                "filled_price": Decimal(str(order.get("price", 0))) if order.get("price") else None,
                "status": self._map_order_status(order.get("status", "")),
                "created_at": datetime.fromisoformat(order.get("enteredTime", "").replace("Z", "+00:00")),
                "updated_at": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"TD Ameritrade get_order_status error: {e}")
            raise

    async def cancel_order(self, broker_order_id: str) -> bool:
        """Cancel an order."""
        try:
            # Get account ID
            response = self.client.get_accounts()
            response.raise_for_status()
            account_id = response.json()[0]["securitiesAccount"]["accountId"]

            # Cancel order
            response = self.client.cancel_order(broker_order_id, account_id)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"TD Ameritrade cancel_order error: {e}")
            return False

    async def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders."""
        try:
            # Get account ID
            response = self.client.get_accounts()
            response.raise_for_status()
            account_id = response.json()[0]["securitiesAccount"]["accountId"]

            # Get orders
            response = self.client.get_orders_by_path(account_id)
            response.raise_for_status()
            orders = response.json()

            result = []
            for order in orders[:limit]:
                leg = order["orderLegCollection"][0]
                instrument = leg["instrument"]
                filled_qty = Decimal(str(order.get("filledQuantity", 0)))
                total_qty = Decimal(str(order.get("quantity", 0)))

                result.append({
                    "broker_order_id": str(order["orderId"]),
                    "ticker": instrument.get("symbol", ""),
                    "side": leg["instruction"].lower().replace("_", " "),
                    "quantity": total_qty,
                    "filled_quantity": filled_qty,
                    "filled_price": Decimal(str(order.get("price", 0))) if order.get("price") else None,
                    "status": self._map_order_status(order.get("status", "")),
                    "created_at": datetime.fromisoformat(order.get("enteredTime", "").replace("Z", "+00:00")),
                    "updated_at": datetime.utcnow(),
                })
            return result
        except Exception as e:
            logger.error(f"TD Ameritrade get_recent_orders error: {e}")
            raise

    # ========================================================================
    # MARKET DATA
    # ========================================================================

    async def get_current_price(self, ticker: str) -> Decimal:
        """Get current market price for a ticker."""
        try:
            response = self.client.get_quote(ticker)
            response.raise_for_status()
            quote = response.json()

            # Use last price or mark price
            if ticker in quote:
                price = quote[ticker].get("lastPrice") or quote[ticker].get("mark", 0)
                return Decimal(str(price))
            else:
                raise ValueError(f"No quote data for {ticker}")
        except Exception as e:
            logger.error(f"TD Ameritrade get_current_price error: {e}")
            raise

    # ========================================================================
    # VALIDATION
    # ========================================================================

    async def validate_connection(self) -> bool:
        """Validate connection."""
        try:
            response = self.client.get_accounts()
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"TD Ameritrade validate_connection error: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _map_order_status(self, td_status: str) -> str:
        """Map TD Ameritrade order status to our standard status."""
        status_map = {
            "AWAITING_PARENT_ORDER": "pending",
            "AWAITING_CONDITION": "pending",
            "AWAITING_MANUAL_REVIEW": "pending",
            "ACCEPTED": "pending",
            "AWAITING_UR_OUT": "pending",
            "PENDING_ACTIVATION": "pending",
            "QUEUED": "pending",
            "WORKING": "pending",
            "REJECTED": "failed",
            "PENDING_CANCEL": "pending",
            "CANCELED": "cancelled",
            "PENDING_REPLACE": "pending",
            "REPLACED": "cancelled",
            "FILLED": "filled",
            "EXPIRED": "cancelled",
        }
        return status_map.get(td_status.upper(), "pending")
