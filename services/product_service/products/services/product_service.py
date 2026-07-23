from django.conf import settings
from products.models import Product, ProductReview
from products.selectors.product_selector import get_product_by_id
from shared.common.client import ServiceClient
from shared.common.exceptions import BadRequestError

_user_client = ServiceClient(
    base_url=settings.USER_SERVICE_URL,
    service_key=settings.SERVICE_KEY,
)


def update_stock(product_id: int, quantity_change: int) -> Product:
    product = get_product_by_id(product_id)
    new_quantity = product.stock_quantity + quantity_change

    if new_quantity < 0:
        raise BadRequestError("Insufficient stock available.")

    product.stock_quantity = new_quantity
    if new_quantity == 0:
        product.status = 'inactive'
    product.save()
    return product


def create_review(product_id: int, user_id: int, rating: int,
                  title: str, comment: str) -> ProductReview:
    _user_client.get(f'/api/v1/users/{user_id}/')

    if ProductReview.objects.filter(
        product_id=product_id, user_id=user_id
    ).exists():
        raise BadRequestError("You have already reviewed this product.")

    return ProductReview.objects.create(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        title=title,
        comment=comment,
    )
