"""Auto-generated from TypeScript type: CreateApiKeyResponse"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CreateApiKeyResponse:
    key_id: str
    key: str

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["keyId"] = self.key_id
        data["key"] = self.key
        return data