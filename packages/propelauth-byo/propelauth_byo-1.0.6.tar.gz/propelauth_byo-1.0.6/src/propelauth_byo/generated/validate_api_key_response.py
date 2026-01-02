"""Auto-generated from TypeScript type: ValidateApiKeyResponse"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .serde_json.json_value import JsonValue


@dataclass
class ValidateApiKeyResponse:
    key_id: str
    metadata: JsonValue
    scopes: List[str]
    user_id: Optional[str] = None
    owner_id: Optional[str] = None

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["keyId"] = self.key_id
        data["metadata"] = self.metadata
        data["scopes"] = self.scopes
        if self.user_id is not None:
            data["userId"] = self.user_id
        if self.owner_id is not None:
            data["ownerId"] = self.owner_id
        return data