import base64
import os
from typing import List, Dict, Any, Optional
from .base import BaseModule

class TradesModule(BaseModule):
    """
    Module for Trades and Payouts (v3).
    """

    def list(self, portfolio_id: int, **kwargs) -> List[Dict[str, Any]]:
        """
        List trades for a portfolio.
        """
        data = self.client.get(f"portfolios/{portfolio_id}/trades.json", version="v3", params=kwargs)
        return data.get("trades", [])

    def get(self, trade_id: int) -> Dict[str, Any]:
        """
        Get details for a specific trade.
        """
        return self.client.get(f"trades/{trade_id}.json", version="v3")

    def create(self, portfolio_id: int, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new trade.
        """
        # Trade data should include holding_id or instrument_id
        # Version 3 expects trades in specific format
        return self.client.post("trades.json", version="v3", data={"trade": trade_data})

    def update(self, trade_id: int, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing trade.
        """
        return self.client.put(f"trades/{trade_id}.json", version="v3", data={"trade": trade_data})

    def delete(self, trade_id: int) -> bool:
        """
        Delete a trade.
        """
        self.client.delete(f"trades/{trade_id}.json", version="v3")
        return True

    # Payouts (Dividends)
    
    def list_payouts(self, holding_id: int) -> List[Dict[str, Any]]:
        """
        List payouts for a specific holding.
        """
        data = self.client.get(f"holdings/{holding_id}/payouts", version="v3")
        return data.get("payouts", [])

    def create_payout(self, holding_id: int, payout_data: Dict[str, Any], attachment_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new payout for a holding.
        
        Args:
            holding_id: ID of the holding.
            payout_data: Dictionary containing payout details (amount, transaction_date, etc).
            attachment_path: Optional local path to a file to attach (PDF, Image).
        """
        payload = {"payout": payout_data.copy()}
        payload["payout"]["holding_id"] = holding_id
        
        if attachment_path:
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment file not found: {attachment_path}")
            
            payload["payout"]["file_attachment"] = self._encode_file(attachment_path)
            payload["payout"]["file_name"] = os.path.basename(attachment_path)
            
        return self.client.post("payouts.json", version="v2", data=payload)

    def _encode_file(self, file_path: str) -> str:
        """Encode a file as a Base64 string."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def update_payout(self, payout_id: int, payout_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing payout.
        """
        return self.client.put(f"payouts/{payout_id}", version="v3", data={"payout": payout_data})

    def delete_payout(self, payout_id: int) -> bool:
        """
        Delete a payout.
        """
        self.client.delete(f"payouts/{payout_id}", version="v3")
        return True
