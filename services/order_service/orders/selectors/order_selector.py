from orders.models import Order, OrderItem
from shared.common.exceptions import NotFoundError


def get_order_by_id(order_id: int, user_id: int = None):
    from django.db.models import Prefetch
    qs = Order.objects.prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.all())
    )
    try:
        if user_id:
            return qs.get(id=order_id, user_id=user_id)
        return qs.get(id=order_id)
    except Order.DoesNotExist:
        raise NotFoundError(f"Order with id {order_id} not found.")


def list_user_orders(user_id: int, status: str = None):
    qs = Order.objects.filter(user_id=user_id)
    if status:
        qs = qs.filter(status=status)
    return qs.order_by('-created_at')


def list_all_orders(status: str = None):
    qs = Order.objects.all()
    if status:
        qs = qs.filter(status=status)
    return qs.order_by('-created_at')
