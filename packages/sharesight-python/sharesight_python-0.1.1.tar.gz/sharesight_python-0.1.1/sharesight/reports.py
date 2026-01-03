from typing import Dict, Any, Optional
from .base import BaseModule

class ReportsModule(BaseModule):
    """
    Module for complex reports (v2.1).
    """

    def get_performance(self, portfolio_id: int, start_date: str, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance report.
        """
        params = {"start_date": start_date}
        if end_date:
            params["end_date"] = end_date
        return self.client.get(f"portfolios/{portfolio_id}/performance.json", version="v2.1", params=params)

    def get_diversity(self, portfolio_id: int, grouping: Optional[str] = "market") -> Dict[str, Any]:
        """
        Get diversity report.
        """
        params = {"grouping": grouping}
        return self.client.get(f"portfolios/{portfolio_id}/diversity.json", version="v2.1", params=params)

    def get_capital_gains(self, portfolio_id: int, start_date: str, end_date: str, **kwargs) -> Dict[str, Any]:
        """
        Get capital gains report.
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        params.update(kwargs)
        return self.client.get(f"portfolios/{portfolio_id}/capital_gains.json", version="v2.1", params=params)

    def get_tax_report(self, portfolio_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get taxable income report.
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self.client.get(f"portfolios/{portfolio_id}/tax_report.json", version="v2.1", params=params)
