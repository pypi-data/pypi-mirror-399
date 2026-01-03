"""
Ticks resource endpoint
"""

from datetime import datetime
from typing import Optional

from qoery._internal import MarketDataApi
from qoery._internal.rest import ApiException

from ..models import Tick, Response
from ..exceptions import InvalidRequestError, APIError


class TicksResource:
    """Resource for raw tick/swap data"""
    
    def __init__(self, api_client):
        self._api = MarketDataApi(api_client)
    
    def get(
        self,
        *,
        symbol: Optional[str] = None,
        pool: Optional[str] = None,
        limit: int = 100,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        networks: Optional[str] = None,
    ) -> Response:
        """
        Get raw tick-level swap data
        
        Args:
            symbol: Trading pair symbol (e.g., "ETH-USDC"). Provide either symbol OR pool.
            pool: Pool contract address. Faster and cheaper than using symbol.
            limit: Number of ticks to return (1-1000). Default: 100
            from_time: Start time (ISO 8601). Defaults to 1 hour ago.
            to_time: End time (ISO 8601). Defaults to current time.
            networks: Comma-separated networks (e.g., "ethereum,arbitrum").
        
        Returns:
            Response: Response containing list of Tick objects and credits_used
        
        Example:
            >>> ticks = client.ticks.get(symbol="WBTC-USDT", limit=20)
            >>> for tick in ticks:
            ...     print(f"{tick.timestamp}: ${tick.price} ({tick.side})")
            >>> print(f"Credits used: {ticks.credits_used}")
        
        Raises:
            InvalidRequestError: If parameters are invalid
            APIError: If the API returns an error
        """
        if not symbol and not pool:
            raise InvalidRequestError("Either 'symbol' or 'pool' must be provided")
        
        if symbol and pool:
            raise InvalidRequestError("Provide either 'symbol' OR 'pool', not both")
        
        try:
            response = self._api.ticks_get(
                symbol=symbol,
                pool=pool,
                limit=limit,
                var_from=from_time,
                to=to_time,
                networks=networks,
            )
            
            # Convert to clean models
            ticks = [Tick.from_api(t) for t in response.data]
            
            return Response(
                data=ticks,
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
