"""Validation and execution exceptions for Keycase Agent SDK."""

from typing import Optional, Set


class KeycaseError(Exception):
    """Base exception for all Keycase errors."""

    pass


class KeywordDefinitionError(KeycaseError):
    """Raised when a keyword is incorrectly defined."""

    pass


class ParameterValidationError(KeycaseError):
    """Raised when parameter validation fails.

    This error occurs when the incoming execution plan JSON has parameters
    that don't match the keyword's @input_param/@output_param definitions.
    """

    def __init__(
        self,
        keyword_name: str,
        message: str,
        missing_params: Optional[Set[str]] = None,
        unknown_params: Optional[Set[str]] = None,
        expected_params: Optional[Set[str]] = None,
        received_params: Optional[Set[str]] = None,
    ):
        self.keyword_name = keyword_name
        self.missing_params = missing_params or set()
        self.unknown_params = unknown_params or set()
        self.expected_params = expected_params or set()
        self.received_params = received_params or set()

        # Build detailed error message
        details = [f"Keyword '{keyword_name}': {message}"]

        if self.missing_params:
            details.append(
                f"  Missing required parameters: {sorted(self.missing_params)}"
            )

        if self.unknown_params:
            details.append(
                f"  Unknown parameters received: {sorted(self.unknown_params)}"
            )

        if self.expected_params:
            details.append(f"  Expected parameters: {sorted(self.expected_params)}")

        if self.received_params:
            details.append(f"  Received parameters: {sorted(self.received_params)}")

        self.detailed_message = "\n".join(details)
        super().__init__(self.detailed_message)


class ExecutionError(KeycaseError):
    """Raised when keyword execution fails."""

    pass


class AuthenticationError(KeycaseError):
    """Raised when authentication fails."""

    pass


class ConnectionError(KeycaseError):
    """Raised when WebSocket connection fails."""

    pass
