"""Auto-generated from TypeScript type: PatchApiKeyCommand"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .serde_json.json_value import JsonValue


@dataclass
class PatchApiKeyCommand:
    key_id: str
    display_name: Optional[str] = None
    expires_at: Optional[int] = None
    set_to_never_expire: Optional[bool] = None
    metadata: Optional[JsonValue] = None

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["keyId"] = self.key_id
        if self.display_name is not None:
            data["displayName"] = self.display_name
        if self.expires_at is not None:
            data["expiresAt"] = self.expires_at
        if self.set_to_never_expire is not None:
            data["setToNeverExpire"] = self.set_to_never_expire
        if self.metadata is not None:
            data["metadata"] = self.metadata
        return data