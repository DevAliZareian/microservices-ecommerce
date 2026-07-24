from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from services.client import ServiceClient
from middlewares.auth import get_current_user, require_admin, TokenPayload
from config import settings

router = APIRouter(prefix="/api/v1", tags=["Payments"])
client = ServiceClient(settings.payment_service_url)


@router.post("/payments")
async def create_payment(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
):
    body = await request.json()
    return await client.post(
        "/api/v1/payments/", json_body=body, user_id=current_user.user_id
    )


@router.get("/payments/list")
async def list_payments(
    status: Optional[str] = Query(None),
    current_user: TokenPayload = Depends(get_current_user),
):
    params = {}
    if status:
        params["status"] = status
    return await client.get(
        "/api/v1/payments/list/", params=params, user_id=current_user.user_id
    )


@router.get("/payments/{payment_id}")
async def get_payment(
    payment_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.get(
        f"/api/v1/payments/{payment_id}/", user_id=current_user.user_id
    )


@router.get("/payments/by-order/{order_id}")
async def get_payment_by_order(
    order_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.get(
        f"/api/v1/payments/by-order/{order_id}/", user_id=current_user.user_id
    )


@router.get("/admin/payments")
async def admin_list_payments(
    status: Optional[str] = Query(None),
    admin: TokenPayload = Depends(require_admin),
):
    params = {}
    if status:
        params["status"] = status
    return await client.get(
        "/api/v1/admin/payments/", params=params, user_id=admin.user_id
    )


@router.patch("/admin/payments/{payment_id}")
async def admin_update_payment(
    payment_id: int,
    request: Request,
    admin: TokenPayload = Depends(require_admin),
):
    body = await request.json()
    return await client.patch(
        f"/api/v1/admin/payments/{payment_id}/",
        json_body=body,
        user_id=admin.user_id,
    )


@router.get("/admin/payments/{payment_id}/refunds")
async def admin_list_refunds(
    payment_id: int,
    admin: TokenPayload = Depends(require_admin),
):
    return await client.get(
        f"/api/v1/admin/payments/{payment_id}/refunds/", user_id=admin.user_id
    )


@router.post("/admin/payments/{payment_id}/refund")
async def admin_create_refund(
    payment_id: int,
    request: Request,
    admin: TokenPayload = Depends(require_admin),
):
    body = await request.json()
    return await client.post(
        f"/api/v1/admin/payments/{payment_id}/refund/",
        json_body=body,
        user_id=admin.user_id,
    )
