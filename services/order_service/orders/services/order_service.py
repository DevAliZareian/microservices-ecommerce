from decimal import Decimal
from django.conf import settings
from orders.models import Order, OrderItem
from orders.selectors.order_selector import get_order_by_id
from shared.common.client import ServiceClient
from shared.common.exceptions import BadRequestError


_user_client = ServiceClient(
    base_url=settings.USER_SERVICE_URL,
    service_key=settings.SERVICE_KEY,
)
_product_client = ServiceClient(
    base_url=settings.PRODUCT_SERVICE_URL,
    service_key=settings.SERVICE_KEY,
)


def _verify_user(user_id: int):
    _user_client.get(f'/api/v1/users/{user_id}/')


def _get_product(product_id: int) -> dict:
    resp = _product_client.get(f'/api/v1/products/id/{product_id}/')
    data = resp.get('data', {})
    return {
        'id': data.get('id'),
        'name': data.get('name'),
        'slug': data.get('slug'),
        'price': Decimal(str(data.get('price', '0'))),
        'stock': data.get('stock_quantity', 0),
    }


def _reserve_stock(product_id: int, quantity: int):
    _product_client.post(
        f'/api/v1/internal/stock/{product_id}/',
        json={'quantity_change': -quantity},
    )


def create_order(user_id: int, items: list, shipping_address: dict,
                 billing_address: dict = None, notes: str = ''):
    _verify_user(user_id)

    order = Order.objects.create(
        user_id=user_id,
        total=Decimal('0.00'),
        shipping_address=shipping_address,
        billing_address=billing_address or shipping_address,
        notes=notes,
    )

    total = Decimal('0.00')
    for item in items:
        product = _get_product(item['product_id'])
        if product['stock'] < item['quantity']:
            order.delete()
            raise BadRequestError(
                f"Insufficient stock for '{product['name']}'."
            )

        unit_price = product['price']
        subtotal = unit_price * item['quantity']

        OrderItem.objects.create(
            order=order,
            product_id=item['product_id'],
            product_name=product['name'],
            product_slug=product['slug'],
            quantity=item['quantity'],
            unit_price=unit_price,
            subtotal=subtotal,
        )
        total += subtotal

    order.total = total
    order.save()

    for item in items:
        _reserve_stock(item['product_id'], item['quantity'])

    return order


def update_order_status(order_id: int, new_status: str, user_id: int = None):
    order = get_order_by_id(order_id, user_id)

    valid_transitions = {
        Order.STATUS_PENDING: [Order.STATUS_CONFIRMED, Order.STATUS_CANCELLED],
        Order.STATUS_CONFIRMED: [Order.STATUS_PROCESSING, Order.STATUS_CANCELLED],
        Order.STATUS_PROCESSING: [Order.STATUS_SHIPPED, Order.STATUS_CANCELLED],
        Order.STATUS_SHIPPED: [Order.STATUS_DELIVERED],
        Order.STATUS_DELIVERED: [],
        Order.STATUS_CANCELLED: [Order.STATUS_REFUNDED],
        Order.STATUS_REFUNDED: [],
    }

    allowed = valid_transitions.get(order.status, [])
    if new_status not in allowed:
        raise BadRequestError(
            f"Cannot transition from '{order.status}' to '{new_status}'."
        )

    order.status = new_status
    order.save()
    return order


def cancel_order(order_id: int, user_id: int):
    return update_order_status(order_id, Order.STATUS_CANCELLED, user_id)
