"""
Clean, Pythonic data models
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Candle:
    """OHLCV Candle data"""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @classmethod
    def from_api(cls, api_candle):
        """Create from OpenAPI generated model"""
        return cls(
            time=api_candle.time,
            open=api_candle.open,
            high=api_candle.high,
            low=api_candle.low,
            close=api_candle.close,
            volume=api_candle.volume,
        )


@dataclass
class Tick:
    """Raw tick/swap data"""
    id: str
    timestamp: datetime
    price: float
    side: str  # 'buy' or 'sell'
    amount0: str
    amount1: str
    amount_usd: float
    sqrt_price_x96: str
    token0: str
    token1: str
    
    @classmethod
    def from_api(cls, api_tick):
        """Create from OpenAPI generated model"""
        return cls(
            id=api_tick.id,
            timestamp=api_tick.timestamp,
            price=api_tick.price,
            side=api_tick.side,
            amount0=api_tick.amount0,
            amount1=api_tick.amount1,
            amount_usd=api_tick.amount_usd,
            sqrt_price_x96=api_tick.sqrt_price_x96,
            token0=api_tick.token0,
            token1=api_tick.token1,
        )


@dataclass
class Token:
    """Token information"""
    symbol: str
    name: str
    address: str
    decimals: Optional[int] = None
    
    @classmethod
    def from_api(cls, api_token):
        """Create from OpenAPI generated model"""
        return cls(
            symbol=api_token.symbol,
            name=api_token.name,
            address=api_token.address,
            decimals=getattr(api_token, 'decimals', None),
        )


@dataclass
class Pool:
    """Liquidity pool information"""
    id: str
    network: str
    protocol_version: str
    fee_tier: str
    liquidity: str
    sqrt_price: str
    volume_usd: str
    tx_count: str
    tvl_usd: str
    token0: Token
    token1: Token
    
    @classmethod
    def from_api(cls, api_pool):
        """Create from OpenAPI generated model"""
        return cls(
            id=api_pool.id,
            network=api_pool.network,
            protocol_version=api_pool.protocol_version,
            fee_tier=api_pool.fee_tier,
            liquidity=api_pool.liquidity,
            sqrt_price=api_pool.sqrt_price,
            volume_usd=api_pool.volume_usd,
            tx_count=api_pool.tx_count,
            tvl_usd=api_pool.total_value_locked_usd,
            token0=Token.from_api(api_pool.token0),
            token1=Token.from_api(api_pool.token1),
        )


@dataclass
class UsageLimitInfo:
    """Usage limit information for a time period"""
    used: int
    limit: int
    remaining: int
    reset_at: Optional[datetime] = None
    
    @classmethod
    def from_api(cls, api_limit):
        """Create from OpenAPI generated model"""
        return cls(
            used=api_limit.used,
            limit=api_limit.limit,
            remaining=api_limit.remaining,
            reset_at=getattr(api_limit, 'reset_at', None),
        )


@dataclass
class Usage:
    """API usage statistics"""
    credits_minute: UsageLimitInfo
    credits_month: UsageLimitInfo
    api_calls_minute_used: int
    api_calls_month_used: int
    subscription_plan: str
    
    @classmethod
    def from_api(cls, api_usage):
        """Create from OpenAPI generated model"""
        return cls(
            credits_minute=UsageLimitInfo.from_api(api_usage.credits.minute),
            credits_month=UsageLimitInfo.from_api(api_usage.credits.month),
            api_calls_minute_used=api_usage.api_calls.minute.used,
            api_calls_month_used=api_usage.api_calls.month.used,
            subscription_plan=api_usage.subscription_plan,
        )


@dataclass
class Response:
    """Generic API response wrapper"""
    data: any
    credits_used: int
    
    def __iter__(self):
        """Make response iterable if data is a list"""
        if isinstance(self.data, list):
            return iter(self.data)
        raise TypeError("Response data is not iterable")
    
    def __len__(self):
        """Return length if data is a list"""
        if isinstance(self.data, list):
            return len(self.data)
        raise TypeError("Response data does not have a length")

    @property
    def df(self):
        """Get data as a pandas DataFrame"""
        import pandas as pd
        from dataclasses import fields, is_dataclass
        
        if isinstance(self.data, list):
            if not self.data:
                # Handle empty list but preserve columns if possible
                # We can't know the type of items in an empty list easily here
                # unless we passed the type to the Response object.
                # But typically Response.data is typed as List[T].
                # For now return empty DF, user should check .empty
                return pd.DataFrame()
            
            # Convert list of dataclasses to DataFrame
            return pd.DataFrame(self.data)
        elif self.data and is_dataclass(self.data):
             # Handle single object
             return pd.DataFrame([self.data])
        else:
             # Fallback
             return pd.DataFrame()

    def to_df(self):
        """Alias for .df property"""
        return self.df
