"""Auto-generated from TypeScript type: ValidateApiKeyError"""
from dataclasses import dataclass
from typing import Dict, Any, Literal, Union, List, Optional
from .api_key_error import ApiKeyError
from .unexpected_error_details import UnexpectedErrorDetails


@dataclass
class ValidateApiKeyErrorInvalidApiKeyError:
    details: ApiKeyError
    type: Literal["InvalidApiKeyError"] = "InvalidApiKeyError"

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["details"] = self.details
        data["type"] = self.type
        return data



@dataclass
class ValidateApiKeyErrorUnexpectedError:
    details: UnexpectedErrorDetails
    type: Literal["UnexpectedError"] = "UnexpectedError"

    def _to_request(self) -> Dict[str, Any]:
        """Convert dataclass to request format with camelCase field names."""
        data: Dict[str, Any] = {}
        data["details"] = self.details
        data["type"] = self.type
        return data




ValidateApiKeyError = Union[
    ValidateApiKeyErrorInvalidApiKeyError,
    ValidateApiKeyErrorUnexpectedError
]

# Export all types for client imports
__all__ = [
    'ValidateApiKeyError',
    'ValidateApiKeyErrorInvalidApiKeyError',
    'ValidateApiKeyErrorUnexpectedError',
]

# Re-export UnexpectedErrorDetails if it was imported
__all__.append('UnexpectedErrorDetails')
