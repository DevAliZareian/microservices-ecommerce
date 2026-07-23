import httpx
from shared.common.exceptions import (
    ServiceUnavailableError,
    NotFoundError,
    BadRequestError,
)


class ServiceClient:
    def __init__(self, base_url: str = None, timeout: int = 10, service_key: str = None):
        self.base_url = base_url
        self.timeout = timeout
        self.service_key = service_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            headers = {'Content-Type': 'application/json'}
            if self.service_key:
                headers['X-Service-Key'] = self.service_key
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client

    def _request(self, method: str, path: str, **kwargs):
        try:
            response = self.client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise ServiceUnavailableError(
                f"Service at {self.base_url} timed out."
            )
        except httpx.ConnectError:
            raise ServiceUnavailableError(
                f"Cannot connect to service at {self.base_url}."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError("Resource not found in upstream service.")
            elif e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                except Exception:
                    error_data = {'detail': 'Bad request'}
                raise BadRequestError(
                    error_data.get('errors', error_data.get('detail', 'Bad request to upstream service.'))
                )
            raise ServiceUnavailableError(
                f"Upstream service returned {e.response.status_code}."
            )

    def get(self, path: str, **kwargs):
        return self._request('GET', path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._request('POST', path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._request('PUT', path, **kwargs)

    def patch(self, path: str, **kwargs):
        return self._request('PATCH', path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request('DELETE', path, **kwargs)

    def close(self):
        if self._client:
            self._client.close()


class UserServiceClient(ServiceClient):
    def __init__(self):
        from django.conf import settings
        super().__init__(
            base_url=getattr(settings, 'USER_SERVICE_URL', 'http://user_service:8000')
        )

    def get_user(self, user_id: int):
        return self.get(f'/api/v1/users/{user_id}/')

    def get_user_by_username(self, username: str):
        return self.get(f'/api/v1/users/by-username/{username}/')

    def verify_user_exists(self, user_id: int) -> bool:
        try:
            self.get_user(user_id)
            return True
        except NotFoundError:
            return False
