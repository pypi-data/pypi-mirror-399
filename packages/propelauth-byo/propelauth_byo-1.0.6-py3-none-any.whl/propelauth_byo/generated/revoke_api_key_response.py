"""Auto-generated from TypeScript type: RevokeApiKeyResponse"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RevokeApiKeyResponse:
    pass

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        return data