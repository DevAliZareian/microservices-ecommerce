from rest_framework.response import Response
from rest_framework import status

def api_response(success: bool = True, data=None, errors=None,
                 http_status: int = status.HTTP_200_OK) -> Response:
    body = {
        "success": success,
        "data": data if data is not None else {},
        "errors": errors,
    }
    return Response(body, status=http_status)

def success_response(data=None, http_status=status.HTTP_200_OK) -> Response:
    return api_response(True, data=data, http_status=http_status)

def error_response(errors=None, http_status=status.HTTP_400_BAD_REQUEST) -> Response:
    return api_response(False, errors=errors, http_status=http_status)