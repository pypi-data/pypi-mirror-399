"""Auto-generated from TypeScript type: GetApiKeysResponse"""
from dataclasses import dataclass
from typing import Dict, Any, List
from .api_key_full_metadata_response import ApiKeyFullMetadataResponse


@dataclass
class GetApiKeysResponse:
    api_keys: List[ApiKeyFullMetadataResponse]
    page_number: int
    page_size: int
    total_results: int

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["apiKeys"] = [item._to_request() for item in self.api_keys]
        data["pageNumber"] = self.page_number
        data["pageSize"] = self.page_size
        data["totalResults"] = self.total_results
        return data