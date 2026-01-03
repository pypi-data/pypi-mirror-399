from typing import List, Dict, Any
from .base import BaseModule

class MarketModule(BaseModule):
    """
    Module for Metadata and Market data (v3).
    """

    def list_markets(self) -> List[Dict[str, Any]]:
        """
        List all supported markets.
        """
        data = self.client.get("markets", version="v3")
        return data.get("markets", [])

    def list_currencies(self) -> List[Dict[str, Any]]:
        """
        List all supported currencies.
        """
        data = self.client.get("currencies", version="v3")
        return data.get("currencies", [])

    def list_countries(self) -> List[Dict[str, Any]]:
        """
        List all supported countries.
        """
        data = self.client.get("countries", version="v3")
        return data.get("countries", [])
