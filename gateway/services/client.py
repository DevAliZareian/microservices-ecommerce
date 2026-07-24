import httpx
from typing import Optional
from fastapi import HTTPException, status


class ServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _request(
        self,
        method: str,
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        if user_id:
            request_headers["X-User-Id"] = str(user_id)

        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=params,
                    json=json_body,
                )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Upstream service timed out",
                )
            except httpx.ConnectError:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Cannot connect to upstream service",
                )
            except httpx.HTTPStatusError as e:
                try:
                    error_detail = e.response.json()
                except Exception:
                    error_detail = {"detail": e.response.text}
                raise HTTPException(
                    status_code=e.response.status_code, detail=error_detail
                )

    async def get(
        self,
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        return await self._request("GET", path, headers=headers, params=params, user_id=user_id)

    async def post(
        self,
        path: str,
        json_body: Optional[dict] = None,
        headers: Optional[dict] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        return await self._request("POST", path, headers=headers, json_body=json_body, user_id=user_id)

    async def put(
        self,
        path: str,
        json_body: Optional[dict] = None,
        headers: Optional[dict] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        return await self._request("PUT", path, headers=headers, json_body=json_body, user_id=user_id)

    async def patch(
        self,
        path: str,
        json_body: Optional[dict] = None,
        headers: Optional[dict] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        return await self._request("PATCH", path, headers=headers, json_body=json_body, user_id=user_id)

    async def delete(
        self,
        path: str,
        headers: Optional[dict] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        return await self._request("DELETE", path, headers=headers, user_id=user_id)
