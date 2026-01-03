"""
Account resource endpoint
"""

from qoery._internal import AccountApi
from qoery._internal.rest import ApiException

from ..models import Usage
from ..exceptions import InvalidRequestError, APIError


class AccountResource:
    """Resource for account and usage information"""
    
    def __init__(self, api_client):
        self._api = AccountApi(api_client)
    
    def usage(self) -> Usage:
        """
        Get API usage statistics
        
        Returns:
            Usage: Current usage statistics including credits and API calls
        
        Example:
            >>> usage = client.account.usage()
            >>> print(f"Plan: {usage.subscription_plan}")
            >>> print(f"Credits used: {usage.credits_month.used}/{usage.credits_month.limit}")
            >>> print(f"Remaining: {usage.credits_month.remaining}")
        
        Raises:
            InvalidRequestError: If API key is invalid
            APIError: If the API returns an error
        """
        try:
            response = self._api.usage_get()
            return Usage.from_api(response)
            
        except ApiException as e:
            if e.status == 401:
                raise InvalidRequestError("Invalid API key")
            elif e.status == 429:
                raise InvalidRequestError("Rate limit exceeded")
            else:
                raise APIError(f"API error: {e}", status_code=e.status)
    
    def get_usage(self) -> Usage:
        """Alias for usage() method"""
        return self.usage()
