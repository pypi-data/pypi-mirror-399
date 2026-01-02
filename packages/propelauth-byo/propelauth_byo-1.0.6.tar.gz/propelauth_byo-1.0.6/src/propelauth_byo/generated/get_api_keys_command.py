"""Auto-generated from TypeScript type: GetApiKeysCommand"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .api_key_status import ApiKeyStatus


@dataclass
class GetApiKeysCommand:
    user_id: Optional[str] = None
    owner_id: Optional[str] = None
    page_number: Optional[int] = None
    page_size: Optional[int] = None
    prefix: Optional[str] = None
    status: Optional[ApiKeyStatus] = None

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        if self.user_id is not None:
            data["userId"] = self.user_id
        if self.owner_id is not None:
            data["ownerId"] = self.owner_id
        if self.page_number is not None:
            data["pageNumber"] = self.page_number
        if self.page_size is not None:
            data["pageSize"] = self.page_size
        if self.prefix is not None:
            data["prefix"] = self.prefix
        if self.status is not None:
            data["status"] = self.status
        return data