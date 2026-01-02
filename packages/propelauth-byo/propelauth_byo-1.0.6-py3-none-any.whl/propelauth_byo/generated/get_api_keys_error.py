"""Auto-generated from TypeScript type: GetApiKeysError"""
from dataclasses import dataclass
from typing import Dict, Any, Literal, Union, List, Optional
from .unexpected_error_details import UnexpectedErrorDetails

@dataclass
class GetApiKeysErrorInvalidQueryFieldDetails:
    field: str
    message: str

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["field"] = self.field
        data["message"] = self.message
        return data



@dataclass
class GetApiKeysErrorInvalidQueryField:
    details: GetApiKeysErrorInvalidQueryFieldDetails
    type: Literal["InvalidQueryField"] = "InvalidQueryField"

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["details"] = self.details._to_request()
        data["type"] = self.type
        return data



@dataclass
class GetApiKeysErrorUserNotFound:
    type: Literal["UserNotFound"] = "UserNotFound"

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["type"] = self.type
        return data



@dataclass
class GetApiKeysErrorUnexpectedError:
    details: UnexpectedErrorDetails
    type: Literal["UnexpectedError"] = "UnexpectedError"

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["details"] = self.details
        data["type"] = self.type
        return data




GetApiKeysError = Union[
    GetApiKeysErrorInvalidQueryField,
    GetApiKeysErrorUserNotFound,
    GetApiKeysErrorUnexpectedError
]

# Export all types for client imports
__all__ = [
    'GetApiKeysError',
    'GetApiKeysErrorInvalidQueryField',
    'GetApiKeysErrorUserNotFound',
    'GetApiKeysErrorUnexpectedError',
    'GetApiKeysErrorInvalidQueryFieldDetails',
]

# Re-export UnexpectedErrorDetails if it was imported
__all__.append('UnexpectedErrorDetails')
