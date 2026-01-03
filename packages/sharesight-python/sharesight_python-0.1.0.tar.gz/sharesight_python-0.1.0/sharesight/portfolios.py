from typing import List, Dict, Any, Optional
from .base import BaseModule

class PortfoliosModule(BaseModule):
    """
    Module for Portfolio management.
    """
    
    def list(self) -> List[Dict[str, Any]]:
        """
        List all portfolios (v2).
        Returns basic info like id, name, currency_code.
        """
        # Note: v3 list is also available but v2 is stable for core list
        data = self.client.get("portfolios.json", version="v2")
        # Standardize response - v2 can be a list or wrapped in 'portfolios'
        if isinstance(data, dict) and "portfolios" in data:
            return data["portfolios"]
        return data

    def get(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Get detailed portfolio information (v3).
        """
        return self.client.get(f"portfolios/{portfolio_id}", version="v3")

    def get_valuation(self, portfolio_id: int, balance_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio valuation (v2).
        """
        params = {}
        if balance_date:
            params["balance_date"] = balance_date
        return self.client.get(f"portfolios/{portfolio_id}/valuation.json", version="v2", params=params)

    def create(self, name: str, currency: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new portfolio (v2).
        """
        data = {
            "name": name,
            "currency_code": currency
        }
        data.update(kwargs)
        return self.client.post("portfolios.json", version="v2", data=data)

    def update(self, portfolio_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update portfolio settings (v2).
        """
        return self.client.put(f"portfolios/{portfolio_id}.json", version="v2", data=data)

    def delete(self, portfolio_id: int) -> bool:
        """
        Delete a portfolio (v2).
        """
        self.client.delete(f"portfolios/{portfolio_id}.json", version="v2")
        return True
