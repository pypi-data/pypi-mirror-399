"""Auto-generated from TypeScript type: RevokeApiKeyCommand"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RevokeApiKeyCommand:
    key_id: str

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["keyId"] = self.key_id
        return data