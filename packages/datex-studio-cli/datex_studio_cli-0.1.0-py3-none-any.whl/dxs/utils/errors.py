"""Custom exception classes for the Datex Studio CLI."""

from typing import Any


class DxsError(Exception):
    """Base exception for all Datex Studio CLI errors.

    Attributes:
        code: Machine-readable error code (e.g., "DXS-AUTH-001").
        message: Human-readable error message.
        details: Additional context about the error.
        suggestions: List of actionable suggestions to resolve the error.
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: Any = None,
        suggestions: list[str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        self.suggestions = suggestions or []
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for output formatting."""
        result: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        if self.suggestions:
            result["suggestions"] = self.suggestions
        return result


class AuthenticationError(DxsError):
    """Raised when authentication fails or token is invalid/expired."""

    def __init__(
        self,
        message: str,
        code: str = "DXS-AUTH-001",
        details: Any = None,
        suggestions: list[str] | None = None,
    ) -> None:
        if suggestions is None:
            suggestions = ["Run 'dxs auth login' to authenticate"]
        super().__init__(code=code, message=message, details=details, suggestions=suggestions)


class ConfigurationError(DxsError):
    """Raised when configuration is missing or invalid."""

    def __init__(
        self,
        message: str,
        code: str = "DXS-CONFIG-001",
        details: Any = None,
        suggestions: list[str] | None = None,
    ) -> None:
        if suggestions is None:
            suggestions = ["Run 'dxs config list' to view current configuration"]
        super().__init__(code=code, message=message, details=details, suggestions=suggestions)


class ApiError(DxsError):
    """Raised when API request fails."""

    def __init__(
        self,
        message: str,
        code: str = "DXS-API-001",
        status_code: int | None = None,
        details: Any = None,
        suggestions: list[str] | None = None,
    ) -> None:
        self.status_code = status_code
        if details is None and status_code is not None:
            details = {"status_code": status_code}
        elif status_code is not None:
            if isinstance(details, dict):
                details["status_code"] = status_code
        super().__init__(code=code, message=message, details=details, suggestions=suggestions)


class ValidationError(DxsError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        code: str = "DXS-VAL-001",
        details: Any = None,
        suggestions: list[str] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, suggestions=suggestions)


class NotFoundError(DxsError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str | int,
        code: str = "DXS-404-001",
        details: Any = None,
        suggestions: list[str] | None = None,
    ) -> None:
        message = f"{resource_type} '{resource_id}' not found"
        if details is None:
            details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(code=code, message=message, details=details, suggestions=suggestions)
