"""Auto-generated from TypeScript type: CreateApiKeyCommand"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .serde_json.json_value import JsonValue


@dataclass
class CreateApiKeyCommand:
    prefix: Optional[str] = None
    display_name: Optional[str] = None
    expires_at: Optional[int] = None
    metadata: Optional[JsonValue] = None
    user_id: Optional[str] = None
    owner_id: Optional[str] = None
    scopes: Optional[List[str]] = None

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        if self.prefix is not None:
            data["prefix"] = self.prefix
        if self.display_name is not None:
            data["displayName"] = self.display_name
        if self.expires_at is not None:
            data["expiresAt"] = self.expires_at
        if self.metadata is not None:
            data["metadata"] = self.metadata
        if self.user_id is not None:
            data["userId"] = self.user_id
        if self.owner_id is not None:
            data["ownerId"] = self.owner_id
        if self.scopes is not None:
            data["scopes"] = self.scopes
        return data