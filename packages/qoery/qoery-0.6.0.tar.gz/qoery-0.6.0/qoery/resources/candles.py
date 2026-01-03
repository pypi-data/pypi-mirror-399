"""
Candles resource endpoint
"""

from datetime import datetime
from typing import Optional, List

from qoery._internal import MarketDataApi
from qoery._internal.rest import ApiException

from ..models import Candle, Response
from ..exceptions import InvalidRequestError, APIError


class CandlesResource:
    """Resource for OHLCV candles data"""
    
    def __init__(self, api_client):
        self._api = MarketDataApi(api_client)
    
    def get(
        self,
        *,
        symbol: Optional[str] = None,
        pool: Optional[str] = None,
        interval: str = "15m",
        limit: int = 10,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        networks: Optional[str] = None,
    ) -> Response:
        """
        Get OHLCV candles for a trading pair
        
        Args:
            symbol: Trading pair symbol (e.g., "ETH-USDC"). Provide either symbol OR pool.
            pool: Pool contract address. Faster and cheaper than using symbol.
            interval: Candle interval (e.g., "1m", "5m", "15m", "1h", "1d"). Default: "15m"
            limit: Number of candles to return (1-100). Default: 10
            from_time: Start time (ISO 8601). Defaults to calculated based on interval and limit.
            to_time: End time (ISO 8601). Defaults to current time.
            networks: Comma-separated networks (e.g., "ethereum,arbitrum").
        
        Returns:
            Response: Response containing list of Candle objects and credits_used
        
        Example:
            >>> candles = client.candles.get(symbol="ETH-USDC", interval="15m", limit=10)
            >>> for candle in candles:
            ...     print(f"{candle.time}: ${candle.close}")
            >>> print(f"Credits used: {candles.credits_used}")
        
        Raises:
            InvalidRequestError: If parameters are invalid
            APIError: If the API returns an error
        """
        if not symbol and not pool:
            raise InvalidRequestError("Either 'symbol' or 'pool' must be provided")
        
        if symbol and pool:
            raise InvalidRequestError("Provide either 'symbol' OR 'pool', not both")
        
        try:
            response = self._api.candles_get(
                symbol=symbol,
                pool=pool,
                interval=interval,
                limit=limit,
                var_from=from_time,
                to=to_time,
                networks=networks,
            )
            
            # Convert to clean models
            candles = [Candle.from_api(c) for c in response.data]
            
            return Response(
                data=candles,
                credits_used=response.credits_used,
            )
            
        except ApiException as e:
            if e.status == 400:
                raise InvalidRequestError(str(e))
            elif e.status == 401:
                raise InvalidRequestError("Invalid API key")
            elif e.status == 429:
                raise InvalidRequestError("Rate limit exceeded")
            else:
                raise APIError(f"API error: {e}", status_code=e.status)
    
    def list(self, **kwargs) -> Response:
        """Alias for get() method"""
        return self.get(**kwargs)
