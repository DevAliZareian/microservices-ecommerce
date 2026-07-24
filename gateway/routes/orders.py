from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from services.client import ServiceClient
from middlewares.auth import get_current_user, require_admin, TokenPayload
from config import settings

router = APIRouter(prefix="/api/v1", tags=["Orders"])
client = ServiceClient(settings.order_service_url)


@router.post("/orders")
async def create_order(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
):
    body = await request.json()
    return await client.post(
        "/api/v1/orders/", json_body=body, user_id=current_user.user_id
    )


@router.get("/orders/list")
async def list_orders(
    status: Optional[str] = Query(None),
    current_user: TokenPayload = Depends(get_current_user),
):
    params = {}
    if status:
        params["status"] = status
    return await client.get(
        "/api/v1/orders/list/", params=params, user_id=current_user.user_id
    )


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.get(
        f"/api/v1/orders/{order_id}/", user_id=current_user.user_id
    )


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.post(
        f"/api/v1/orders/{order_id}/cancel/", user_id=current_user.user_id
    )


@router.get("/admin/orders")
async def admin_list_orders(
    status: Optional[str] = Query(None),
    admin: TokenPayload = Depends(require_admin),
):
    params = {}
    if status:
        params["status"] = status
    return await client.get(
        "/api/v1/admin/orders/", params=params, user_id=admin.user_id
    )


@router.patch("/admin/orders/{order_id}")
async def admin_update_order(
    order_id: int,
    request: Request,
    admin: TokenPayload = Depends(require_admin),
):
    body = await request.json()
    return await client.patch(
        f"/api/v1/admin/orders/{order_id}/",
        json_body=body,
        user_id=admin.user_id,
    )
