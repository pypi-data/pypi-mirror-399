"""Custom exceptions for Keycase Agent SDK."""

from .auth_exceptions import AuthTokenMissing, LoginError
from .validation_exceptions import (
    AuthenticationError,
    ConnectionError,
    ExecutionError,
    KeycaseError,
    KeywordDefinitionError,
    ParameterValidationError,
)

__all__ = [
    # Auth exceptions
    "LoginError",
    "AuthTokenMissing",
    # Validation exceptions
    "KeycaseError",
    "KeywordDefinitionError",
    "ParameterValidationError",
    "ExecutionError",
    "AuthenticationError",
    "ConnectionError",
]
