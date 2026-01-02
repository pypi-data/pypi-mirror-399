"""Auto-generated from TypeScript type: ValidateApiKeyCommand"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ValidateApiKeyCommand:
    key: str

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["key"] = self.key
        return data