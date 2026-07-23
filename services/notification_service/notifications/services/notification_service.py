from django.utils import timezone
from notifications.models import Notification
from notifications.selectors.notification_selector import get_notification_by_id
from shared.common.exceptions import BadRequestError


def create_notification(user_id: int, type: str, title: str,
                        message: str, link: str = ''):
    valid_types = [c[0] for c in Notification.TYPE_CHOICES]
    if type not in valid_types:
        raise BadRequestError(f"Invalid notification type '{type}'.")

    return Notification.objects.create(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
    )


def mark_as_read(notification_id: int, user_id: int):
    notification = get_notification_by_id(notification_id, user_id)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    return notification


def mark_all_as_read(user_id: int):
    return Notification.objects.filter(
        user_id=user_id, is_read=False
    ).update(is_read=True, read_at=timezone.now())


def delete_notification(notification_id: int, user_id: int):
    notification = get_notification_by_id(notification_id, user_id)
    notification.delete()


def send_order_notification(order_id: int, user_id: int, order_status: str):
    type_map = {
        'confirmed': Notification.TYPE_ORDER_CONFIRMED,
        'shipped': Notification.TYPE_ORDER_SHIPPED,
        'delivered': Notification.TYPE_ORDER_DELIVERED,
        'cancelled': Notification.TYPE_ORDER_CANCELLED,
    }
    title_map = {
        'confirmed': 'Order Confirmed',
        'shipped': 'Order Shipped',
        'delivered': 'Order Delivered',
        'cancelled': 'Order Cancelled',
    }
    message_map = {
        'confirmed': f'Your order #{order_id} has been confirmed.',
        'shipped': f'Your order #{order_id} has been shipped.',
        'delivered': f'Your order #{order_id} has been delivered.',
        'cancelled': f'Your order #{order_id} has been cancelled.',
    }

    ntype = type_map.get(order_status)
    if not ntype:
        raise BadRequestError(
            f"Unknown order status '{order_status}' for notification."
        )

    return create_notification(
        user_id=user_id,
        type=ntype,
        title=title_map[order_status],
        message=message_map[order_status],
        link=f'/orders/{order_id}/',
    )
