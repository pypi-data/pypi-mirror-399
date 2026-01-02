"""Auto-generated from TypeScript type: ApiKeyFullMetadataResponse"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .serde_json.json_value import JsonValue


@dataclass
class ApiKeyFullMetadataResponse:
    key_id: str
    created_at: int
    scopes: List[str]
    expires_at: int
    last_active_at: int
    metadata: JsonValue
    display_name: Optional[str] = None
    user_id: Optional[str] = None
    owner_id: Optional[str] = None

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["keyId"] = self.key_id
        data["createdAt"] = self.created_at
        data["scopes"] = self.scopes
        data["expiresAt"] = self.expires_at
        data["lastActiveAt"] = self.last_active_at
        data["metadata"] = self.metadata
        if self.display_name is not None:
            data["displayName"] = self.display_name
        if self.user_id is not None:
            data["userId"] = self.user_id
        if self.owner_id is not None:
            data["ownerId"] = self.owner_id
        return data