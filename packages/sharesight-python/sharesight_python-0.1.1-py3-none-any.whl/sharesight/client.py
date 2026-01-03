from typing import Optional, Dict, Any, List
import httpx
from .auth import OAuthManager, TokenStore
from .exceptions import SharesightAPIError, SharesightRateLimitError
from .portfolios import PortfoliosModule
from .holdings import HoldingsModule
from .trades import TradesModule
from .reports import ReportsModule
from .market import MarketModule
from .investments import InvestmentsModule

class SharesightClient:
    """
    The main client for interacting with Sharesight API v2 and v3.
    """
    
    API_V2_BASE = "https://api.sharesight.com/api/v2"
    API_V3_BASE = "https://api.sharesight.com/api/v3"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_store: Optional[TokenStore] = None,
        user_agent: str = "SharesightPythonSDK/1.0"
    ):
        self.auth = OAuthManager(client_id, client_secret, token_store)
        self.user_agent = user_agent
        self._http_client = httpx.Client(
            headers={"User-Agent": self.user_agent},
            timeout=30.0
        )
        
        # Initialize modules
        self.portfolios = PortfoliosModule(self)
        self.holdings = HoldingsModule(self)
        self.trades = TradesModule(self)
        self.reports = ReportsModule(self)
        self.market = MarketModule(self)
        self.investments = InvestmentsModule(self)

    def request(
        self,
        method: str,
        path: str,
        version: str = "v3",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform an authenticated request to the Sharesight API.
        """
        token = self.auth.get_access_token()
        
        base_url = self.API_V3_BASE if version == "v3" else self.API_V2_BASE
        # Handle cases where path might already include version or full URL
        if path.startswith("http"):
            url = path
        else:
            url = f"{base_url}/{path.lstrip('/')}"

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/json"

        try:
            resp = self._http_client.request(
                method,
                url,
                params=params,
                json=json_data,
                headers=headers,
                **kwargs
            )
            
            if resp.status_code == 429:
                raise SharesightRateLimitError("Rate limit exceeded", 429, resp.text)
                
            if resp.status_code == 401:
                # Potential token expiry race condition? Try re-auth once
                self.auth.revoke_token() # Clear invalid token
                token = self.auth.get_access_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = self._http_client.request(method, url, params=params, json=json_data, headers=headers, **kwargs)

            resp.raise_for_status()
            
            # Some v2 endpoints return directly, some wrap in .json() or have specific lists
            return resp.json()
            
        except httpx.HTTPStatusError as e:
            raise SharesightAPIError(
                f"API Request failed: {e.response.text}",
                status_code=e.response.status_code,
                response_body=e.response.text
            ) from e
        except Exception as e:
            raise SharesightAPIError(f"Unexpected error during request: {e}") from e

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.request("POST", path, json_data=data, **kwargs)

    def put(self, path: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.request("PUT", path, json_data=data, **kwargs)

    def patch(self, path: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.request("PATCH", path, json_data=data, **kwargs)

    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("DELETE", path, **kwargs)
