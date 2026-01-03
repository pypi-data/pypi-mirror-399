from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SharesightClient

class BaseModule:
    """Base class for API modules."""
    def __init__(self, client: 'SharesightClient'):
        self.client = client
