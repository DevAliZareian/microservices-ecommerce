from rest_framework.exceptions import APIException

class ServiceError(APIException):
    default_detail = 'A service error occurred.'
    default_code = 'service_error'

class NotFoundError(ServiceError):
    status_code = 404
    default_detail = 'The requested resource was not found.'
    default_code = 'not_found'

class ConflictError(ServiceError):
    status_code = 409
    default_detail = 'Resource already exists.'
    default_code = 'conflict'

class BadRequestError(ServiceError):
    status_code = 400
    default_detail = 'Invalid request.'
    default_code = 'bad_request'

class AuthenticationFailedError(ServiceError):
    status_code = 401
    default_detail = 'Authentication credentials were not provided or are invalid.'
    default_code = 'authentication_failed'

class PermissionDeniedError(ServiceError):
    status_code = 403
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'