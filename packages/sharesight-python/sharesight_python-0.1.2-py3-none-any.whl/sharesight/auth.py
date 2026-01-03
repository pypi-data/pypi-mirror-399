import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
import httpx
from .exceptions import SharesightAuthError

class TokenStore:
    """Base class for token persistence."""
    def load(self) -> Dict[str, Any]:
        return {}
    
    def save(self, token_data: Dict[str, Any]):
        pass

class FileTokenStore(TokenStore):
    """File-based token persistence."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
        
    def save(self, token_data: Dict[str, Any]):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(token_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save token to {self.filepath}: {e}")

class OAuthManager:
    """Manages Sharesight OAuth2 authentication."""
    
    TOKEN_URL = "https://api.sharesight.com/oauth2/token"
    REVOKE_URL = "https://api.sharesight.com/oauth2/revoke"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_store: Optional[TokenStore] = None,
        redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob"
    ):
        self.client_id = client_id or os.getenv("SHARESIGHT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SHARESIGHT_CLIENT_SECRET")
        self.token_store = token_store
        self.redirect_uri = redirect_uri
        
        if not self.client_id or not self.client_secret:
            raise SharesightAuthError("SHARESIGHT_CLIENT_ID and SHARESIGHT_CLIENT_SECRET are required.")
            
        self._token_data = self.token_store.load() if self.token_store else {}

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self._is_token_valid():
            return self._token_data["access_token"]
            
        if "refresh_token" in self._token_data:
            return self.refresh_access_token()
            
        return self.authenticate_client_credentials()

    def _is_token_valid(self) -> bool:
        """Check if the current cached token is valid."""
        if not self._token_data.get("access_token"):
            return False
            
        expires_at = self._token_data.get("expires_at")
        if not expires_at:
            return False
            
        # Buffering by 2 minutes to avoid race conditions
        return time.time() < (expires_at - 120)

    def authenticate_client_credentials(self) -> str:
        """Perform Client Credentials flow (for headless cloud use)."""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }
        return self._fetch_token(data)

    def refresh_access_token(self) -> str:
        """Refresh the access token using a refresh token."""
        refresh_token = self._token_data.get("refresh_token")
        if not refresh_token:
            raise SharesightAuthError("No refresh token available to refresh session.")
            
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        return self._fetch_token(data)

    def _fetch_token(self, payload: Dict[str, Any]) -> str:
        """Execute token request and update store."""
        try:
            resp = httpx.post(self.TOKEN_URL, data=payload)
            resp.raise_for_status()
            
            token_response = resp.json()
            
            # Sharesight v2/v3 might have slight differences, normalizing here
            self._token_data = {
                "access_token": token_response["access_token"],
                "refresh_token": token_response.get("refresh_token"),
                "expires_at": time.time() + token_response.get("expires_in", 1800),
                "token_type": token_response.get("token_type", "Bearer"),
                "created_at": time.time()
            }
            
            if self.token_store:
                self.token_store.save(self._token_data)
                
            return self._token_data["access_token"]
            
        except httpx.HTTPStatusError as e:
            raise SharesightAuthError(f"Failed to fetch token: {e.response.text}") from e
        except Exception as e:
            raise SharesightAuthError(f"Unexpected error during authentication: {e}") from e

    def revoke_token(self):
        """Revoke the current access token."""
        token = self._token_data.get("access_token")
        if not token:
            return
            
        try:
            httpx.post(self.REVOKE_URL, data={"token": token, "client_id": self.client_id, "client_secret": self.client_secret})
            self._token_data = {}
            if self.token_store:
                self.token_store.save({})
        except Exception:
            pass
