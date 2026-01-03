from typing import List, Dict, Any, Optional
from .base import BaseModule

class InvestmentsModule(BaseModule):
    """
    Module for Custom Investments (v3).
    """

    def list_custom(self, portfolio_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List custom investments.
        
        Args:
            portfolio_id: Optional filter for a specific portfolio.
        """
        params = {}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
            
        data = self.client.get("custom_investments", version="v3", params=params)
        return data.get("custom_investments", [])

    def get_custom(self, investment_id: int) -> Dict[str, Any]:
        """
        Get details for a specific custom investment.
        """
        return self.client.get(f"custom_investments/{investment_id}", version="v3")
