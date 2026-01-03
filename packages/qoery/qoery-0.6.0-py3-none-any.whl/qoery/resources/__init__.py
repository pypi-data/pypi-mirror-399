"""
Resource endpoints for the Qoery SDK
"""

from .candles import CandlesResource
from .ticks import TicksResource
from .pools import PoolsResource
from .account import AccountResource

__all__ = [
    "CandlesResource",
    "TicksResource",
    "PoolsResource",
    "AccountResource",
]
