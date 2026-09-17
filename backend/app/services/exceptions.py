# app/services/exceptions.py


class ServiceError(Exception):
    """Base class for domain-level errors raised by services."""


class NotFoundError(ServiceError):
    """The requested resource does not exist."""


class ValidationError(ServiceError):
    """Input or domain state is invalid."""
