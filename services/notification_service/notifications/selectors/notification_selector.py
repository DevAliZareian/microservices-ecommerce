from notifications.models import Notification
from shared.common.exceptions import NotFoundError


def list_user_notifications(user_id: int, unread_only: bool = False):
    qs = Notification.objects.filter(user_id=user_id)
    if unread_only:
        qs = qs.filter(is_read=False)
    return qs.order_by('-created_at')


def get_unread_count(user_id: int):
    return Notification.objects.filter(
        user_id=user_id, is_read=False
    ).count()


def get_notification_by_id(notification_id: int, user_id: int = None):
    try:
        if user_id:
            return Notification.objects.get(
                id=notification_id, user_id=user_id
            )
        return Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        raise NotFoundError(
            f"Notification with id {notification_id} not found."
        )
