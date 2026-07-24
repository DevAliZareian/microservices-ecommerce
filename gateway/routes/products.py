from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from services.client import ServiceClient
from middlewares.auth import get_current_user, require_admin, TokenPayload
from config import settings

router = APIRouter(prefix="/api/v1", tags=["Products"])
client = ServiceClient(settings.product_service_url)


@router.get("/products")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    ordering: Optional[str] = None,
    current_user: TokenPayload | None = Depends(get_current_user),
):
    params = {"page": page, "page_size": page_size}
    if search:
        params["search"] = search
    if category:
        params["category"] = category
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if ordering:
        params["ordering"] = ordering
    return await client.get("/api/v1/products/", params=params, user_id=current_user.user_id if current_user else None)


@router.get("/products/featured")
async def featured_products():
    return await client.get("/api/v1/products/featured/")


@router.get("/products/{slug}")
async def get_product_by_slug(slug: str):
    return await client.get(f"/api/v1/products/{slug}/")


@router.get("/products/id/{product_id}")
async def get_product_by_id(product_id: int):
    return await client.get(f"/api/v1/products/id/{product_id}/")


@router.get("/categories")
async def list_categories():
    return await client.get("/api/v1/categories/")


@router.get("/reviews/{product_id}")
async def list_reviews(product_id: int):
    return await client.get(f"/api/v1/reviews/{product_id}/")


@router.post("/reviews")
async def create_review(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
):
    body = await request.json()
    return await client.post(
        "/api/v1/reviews/", json_body=body, user_id=current_user.user_id
    )


@router.post("/admin/products")
async def create_product(
    request: Request,
    admin: TokenPayload = Depends(require_admin),
):
    body = await request.json()
    return await client.post(
        "/api/v1/admin/products/", json_body=body, user_id=admin.user_id
    )


@router.put("/admin/products/{product_id}")
async def update_product(
    product_id: int,
    request: Request,
    admin: TokenPayload = Depends(require_admin),
):
    body = await request.json()
    return await client.put(
        f"/api/v1/admin/products/{product_id}/", json_body=body, user_id=admin.user_id
    )
