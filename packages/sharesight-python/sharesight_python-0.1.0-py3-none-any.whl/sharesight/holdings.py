from typing import List, Dict, Any, Optional
from .base import BaseModule

class HoldingsModule(BaseModule):
    """
    Module for Holding management (v3).
    """

    def list(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        List all holdings in a portfolio.
        """
        data = self.client.get(f"portfolios/{portfolio_id}/holdings", version="v3")
        return data.get("holdings", [])

    def get(self, holding_id: int) -> Dict[str, Any]:
        """
        Get detail for a specific holding.
        """
        return self.client.get(f"holdings/{holding_id}", version="v3")

    def update(self, holding_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a holding's settings.
        """
        return self.client.put(f"holdings/{holding_id}", version="v3", data=data)

    def delete(self, holding_id: int) -> bool:
        """
        Delete a holding.
        """
        self.client.delete(f"holdings/{holding_id}", version="v3")
        return True

    def get_valuation(self, holding_id: int) -> Dict[str, Any]:
        """
        Get current valuation for a single holding.
        """
        return self.client.get(f"holdings/{holding_id}/valuation", version="v3")
