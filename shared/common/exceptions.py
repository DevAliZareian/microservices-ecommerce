"""
Custom exceptions shared across all microservices.
Mapped to appropriate HTTP status codes for DRF's exception handler.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class ServiceError(APIException):
    """Base exception for all services."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A service error occurred.'
    default_code = 'service_error'


class NotFoundError(ServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'


class BadRequestError(ServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid request.'
    default_code = 'bad_request'


class ConflictError(ServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource already exists.'
    default_code = 'conflict'


class AuthenticationFailedError(ServiceError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided or are invalid.'
    default_code = 'authentication_failed'


class PermissionDeniedError(ServiceError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class ValidationError(ServiceError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Validation failed.'
    default_code = 'validation_error'


class ServiceUnavailableError(ServiceError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service is temporarily unavailable.'
    default_code = 'service_unavailable'