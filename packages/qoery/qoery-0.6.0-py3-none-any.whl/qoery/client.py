"""
Main client class for the Qoery SDK
"""

import os
from typing import Optional
from dotenv import load_dotenv

from qoery._internal import (
    Configuration,
    ApiClient,
    MarketDataApi,
    SystemApi,
)
from .resources import CandlesResource, TicksResource, PoolsResource, AccountResource
from .exceptions import AuthenticationError


class Client:
    """
    Qoery API Client
    
    Args:
        api_key: Your Qoery API key. If not provided, will look for QOERY_API_KEY env var.
        base_url: API base URL. Defaults to production API.
        timeout: Request timeout in seconds.
    
    Example:
        >>> import qoery
        >>> client = qoery.Client()  # Loads QOERY_API_KEY from .env
        >>> candles = client.candles.get(symbol="ETH-USDC", interval="15m")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.qoery.com/v0",
        timeout: int = 30,
    ):
        # Automatically load .env file if present
        load_dotenv()
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("QOERY_API_KEY")
        
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Either pass it as 'api_key' parameter or set QOERY_API_KEY environment variable."
            )
        
        self.base_url = base_url
        self.timeout = timeout
        
        # Configure the underlying OpenAPI client
        self._config = Configuration(host=base_url)
        self._config.api_key['ApiKeyAuthHeader'] = self.api_key
        
        # Initialize API client
        self._api_client = ApiClient(self._config)
        
        # Initialize resource endpoints
        self.candles = CandlesResource(self._api_client)
        self.ticks = TicksResource(self._api_client)
        self.pools = PoolsResource(self._api_client)
        self.account = AccountResource(self._api_client)
    
    def __enter__(self):
        """Support context manager usage"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context manager"""
        self._api_client.close()
    
    def close(self):
        """Close the API client and clean up resources"""
        self._api_client.close()
    
    def health_check(self) -> dict:
        """
        Check API health status
        
        Returns:
            dict: Health status information
        
        Example:
            >>> client.health_check()
            {'status': 'healthy', 'timestamp': 1704036000}
        """
        api = SystemApi(self._api_client)
        response = api.health_get()
        return {
            'status': response.status,
            'timestamp': response.timestamp
        }
