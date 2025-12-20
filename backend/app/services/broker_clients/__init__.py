"""
Broker API Clients

Factory and imports for all supported broker integrations.
"""

from .base import BaseBrokerClient
from .alpaca_client import AlpacaClient
from .td_ameritrade_client import TDAmeritradeClient
from .interactive_brokers_client import InteractiveBrokersClient

__all__ = [
    "BaseBrokerClient",
    "AlpacaClient",
    "TDAmeritradeClient",
    "InteractiveBrokersClient",
    "get_broker_client",
]


def get_broker_client(broker: str, access_token: str) -> BaseBrokerClient:
    """
    Factory function to get the appropriate broker client.

    Args:
        broker: Broker name ('alpaca', 'td_ameritrade', 'interactive_brokers')
        access_token: Decrypted OAuth access token

    Returns:
        Appropriate broker client instance

    Raises:
        ValueError: If broker is not supported
    """
    broker_map = {
        "alpaca": AlpacaClient,
        "td_ameritrade": TDAmeritradeClient,
        "interactive_brokers": InteractiveBrokersClient,
    }

    client_class = broker_map.get(broker.lower())
    if not client_class:
        raise ValueError(f"Unsupported broker: {broker}")

    return client_class(access_token)
