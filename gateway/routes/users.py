from fastapi import APIRouter, Depends, Request
from services.client import ServiceClient
from middlewares.auth import get_current_user, TokenPayload
from config import settings

router = APIRouter(prefix="/api/v1", tags=["Users"])
client = ServiceClient(settings.user_service_url)


@router.get("/profile")
async def get_profile(current_user: TokenPayload = Depends(get_current_user)):
    return await client.get("/api/v1/profile/", user_id=current_user.user_id)


@router.patch("/profile")
async def update_profile(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
):
    body = await request.json()
    return await client.patch("/api/v1/profile/", json_body=body, user_id=current_user.user_id)


@router.post("/change-password")
async def change_password(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
):
    body = await request.json()
    return await client.post(
        "/api/v1/change-password/", json_body=body, user_id=current_user.user_id
    )


@router.get("/users/me")
async def get_current_user_detail(current_user: TokenPayload = Depends(get_current_user)):
    return await client.get("/api/v1/users/me/", user_id=current_user.user_id)


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.get(f"/api/v1/users/{user_id}/", user_id=current_user.user_id)


@router.get("/users/by-username/{username}")
async def get_user_by_username(
    username: str,
    current_user: TokenPayload = Depends(get_current_user),
):
    return await client.get(
        f"/api/v1/users/by-username/{username}/", user_id=current_user.user_id
    )
