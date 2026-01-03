"""Custom exceptions for the DataHorders CDN SDK."""

from __future__ import annotations

from typing import Any


class DataHordersError(Exception):
    """Base exception for all DataHorders CDN SDK errors."""

    def __init__(
        self, message: str, code: str | None = None, details: Any = None
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            code: Error code from the API.
            details: Additional error details.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """Return repr of the error."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r})"
        )


class AuthenticationError(DataHordersError):
    """Raised when authentication fails (401)."""

    pass


class AuthorizationError(DataHordersError):
    """Raised when authorization fails (403)."""

    pass


class NotFoundError(DataHordersError):
    """Raised when a resource is not found (404)."""

    pass


class ConflictError(DataHordersError):
    """Raised when there is a resource conflict (409)."""

    pass


class ValidationError(DataHordersError):
    """Raised when request validation fails (400)."""

    pass


class RateLimitError(DataHordersError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: Any = None,
        retry_after: int | None = None,
    ) -> None:
        """Initialize the rate limit error.

        Args:
            message: Human-readable error message.
            code: Error code from the API.
            details: Additional error details.
            retry_after: Seconds to wait before retrying.
        """
        super().__init__(message, code, details)
        self.retry_after = retry_after


class ServerError(DataHordersError):
    """Raised when the server returns a 5xx error."""

    pass


class DomainExistsError(ConflictError):
    """Raised when a domain already exists."""

    pass


class DomainInUseError(ConflictError):
    """Raised when a domain is in use and cannot be deleted."""

    pass


class CertificateInUseError(ConflictError):
    """Raised when a certificate is in use and cannot be deleted."""

    pass


class DuplicateCertificateError(ValidationError):
    """Raised when a certificate already exists for a domain."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: Any = None,
        existing_certificate_id: str | None = None,
    ) -> None:
        """Initialize the duplicate certificate error.

        Args:
            message: Human-readable error message.
            code: Error code from the API.
            details: Additional error details.
            existing_certificate_id: ID of the existing certificate.
        """
        super().__init__(message, code, details)
        self.existing_certificate_id = existing_certificate_id


class InvalidCertificateError(ValidationError):
    """Raised when certificate validation fails."""

    pass


class InvalidDomainsError(ValidationError):
    """Raised when specified domains are invalid or unverified."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: Any = None,
        missing_domains: list[str] | None = None,
    ) -> None:
        """Initialize the invalid domains error.

        Args:
            message: Human-readable error message.
            code: Error code from the API.
            details: Additional error details.
            missing_domains: List of invalid domain IDs.
        """
        super().__init__(message, code, details)
        self.missing_domains = missing_domains or []


class CircularUpstreamError(ValidationError):
    """Raised when an upstream would create a circular reference."""

    pass
