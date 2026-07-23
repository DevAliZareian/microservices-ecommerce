"""
Standard API response format used across ALL services.
Every microservice will return identical response structures.
"""
from rest_framework.response import Response
from rest_framework import status


def api_response(
    success: bool = True,
    data=None,
    errors=None,
    message: str = None,
    http_status: int = status.HTTP_200_OK
) -> Response:
    """
    Universal JSON response envelope:
    {
        "success": true/false,
        "message": "optional message",
        "data": { ... } or [],
        "errors": { ... } or null
    }
    """
    body = {
        "success": success,
        "message": message,
        "data": data if data is not None else {},
        "errors": errors,
    }
    # Remove None values for cleaner JSON
    if body['message'] is None:
        del body['message']

    return Response(body, status=http_status)


def success_response(
    data=None,
    message: str = None,
    http_status: int = status.HTTP_200_OK
) -> Response:
    """Shortcut for successful responses."""
    return api_response(
        success=True,
        data=data,
        message=message,
        http_status=http_status
    )


def error_response(
    errors=None,
    message: str = None,
    http_status: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """Shortcut for error responses."""
    return api_response(
        success=False,
        errors=errors,
        message=message,
        http_status=http_status
    )


def paginated_response(
    data=None,
    pagination: dict = None,
    message: str = None,
    http_status: int = status.HTTP_200_OK
) -> Response:
    """
    Response wrapper for paginated data.
    Adds pagination metadata alongside the data.
    """
    response_data = {
        "items": data,
        "pagination": pagination
    }
    return api_response(
        success=True,
        data=response_data,
        message=message,
        http_status=http_status
    )