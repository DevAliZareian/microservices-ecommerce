from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from services.client import ServiceClient
from middlewares.auth import get_current_user, require_admin, TokenPayload
from config import settings

router = APIRouter(prefix="/api/v1", tags=["Notifications"])
client = ServiceClient(settings.notification_service_url)


@router.get("/notifications")
async def list_notifications(
    unread_only: Optional[bool] = Query(False),
    current_user: TokenPayload = Depends(get_current_user),
):
    params = {}
    if unread_only:
        params["unread_only"] = "true"
    return await client.get(
        "/api/v1/notifications/", params=params, user_id=current_user.user_id
    )


@router.get("/notifications/unread-count")
async def unread_count(current_user: TokenPayload = Depends(get_current_user)):
    return await client.get(
        "/api/v1/notifications/unread-count/", user_id=current_user.user_id
    )


@router.get("/notifications/{notification_id}")
async def get_notification(
    notification_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.get(
        f"/api/v1/notifications/{notification_id}/", user_id=current_user.user_id
    )


@router.post("/notifications/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.post(
        f"/api/v1/notifications/{notification_id}/read/", user_id=current_user.user_id
    )


@router.post("/notifications/read-all")
async def mark_all_as_read(current_user: TokenPayload = Depends(get_current_user)):
    return await client.post(
        "/api/v1/notifications/read-all/", user_id=current_user.user_id
    )


@router.delete("/notifications/{notification_id}/delete")
async def delete_notification(
    notification_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.delete(
        f"/api/v1/notifications/{notification_id}/delete/", user_id=current_user.user_id
    )


@router.post("/admin/notifications")
async def admin_create_notification(
    request: Request,
    admin: TokenPayload = Depends(require_admin),
):
    body = await request.json()
    return await client.post(
        "/api/v1/admin/notifications/", json_body=body, user_id=admin.user_id
    )
