"""
Pools resource endpoint
"""

from qoery._internal import DiscoveryApi
from qoery._internal.rest import ApiException

from ..models import Pool, Response
from ..exceptions import InvalidRequestError, APIError


class PoolsResource:
    """Resource for pool discovery"""
    
    def __init__(self, api_client):
        self._api = DiscoveryApi(api_client)
    
    def find(self, symbol: str) -> Response:
        """
        Find liquidity pools for a trading pair
        
        Args:
            symbol: Trading pair symbol (e.g., "ETH-USDC")
        
        Returns:
            Response: Response containing list of Pool objects sorted by liquidity
        
        Example:
            >>> pools = client.pools.find(symbol="ETH-USDC")
            >>> for pool in pools:
            ...     print(f"{pool.network}: {pool.id} (TVL: ${pool.tvl_usd})")
            >>> print(f"Credits used: {pools.credits_used}")
        
        Raises:
            InvalidRequestError: If parameters are invalid
            APIError: If the API returns an error
        """
        if not symbol:
            raise InvalidRequestError("'symbol' is required")
        
        try:
            response = self._api.pools_get(symbol=symbol)
            
            # Convert to clean models
            pools = [Pool.from_api(p) for p in response.data]
            
            return Response(
                data=pools,
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
    
    def search(self, **kwargs) -> Response:
        """Alias for find() method"""
        return self.find(**kwargs)
    
    def list(self, **kwargs) -> Response:
        """Alias for find() method"""
        return self.find(**kwargs)
