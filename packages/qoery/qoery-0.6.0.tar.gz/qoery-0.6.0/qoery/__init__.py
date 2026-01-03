"""
Qoery Python SDK - A developer-friendly wrapper for the Qoery DeFi Data API

Example usage:
    import qoery
    
    # Initialize the client
    client = qoery.Client(api_key="your-api-key")
    
    # Get candles
    candles = client.candles.get(symbol="ETH-USDC", interval="15m", limit=10)
    
    # Get ticks
    ticks = client.ticks.get(symbol="WBTC-USDT", limit=100)
    
    # Find pools
    pools = client.pools.find(symbol="ETH-USDC")
    
    # Check usage
    usage = client.account.usage()
"""

from .client import Client
from .exceptions import (
    QoeryError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    APIError,
)
from .models import Candle, Tick, Pool, Token, Usage

__version__ = "0.6.0"

__all__ = [
    "Client",
    "QoeryError",
    "AuthenticationError",
    "InvalidRequestError",
    "RateLimitError",
    "APIError",
    "Candle",
    "Tick",
    "Pool",
    "Token",
    "Usage",
]
