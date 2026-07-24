from fastapi import APIRouter, Request
from services.client import ServiceClient
from config import settings

router = APIRouter(prefix="/api/v1", tags=["Authentication"])
client = ServiceClient(settings.user_service_url)


@router.post("/register")
async def register(request: Request):
    body = await request.json()
    return await client.post("/api/v1/register/", json_body=body)


@router.post("/login")
async def login(request: Request):
    body = await request.json()
    return await client.post("/api/v1/login/", json_body=body)


@router.post("/token/refresh")
async def token_refresh(request: Request):
    body = await request.json()
    return await client.post("/api/v1/token/refresh/", json_body=body)
