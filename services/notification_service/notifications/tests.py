from django.test import TestCase
from notifications.models import Notification


class NotificationModelTest(TestCase):
    def setUp(self):
        self.notification = Notification.objects.create(
            user_id=1,
            type=Notification.TYPE_ORDER_CONFIRMED,
            title='Order Confirmed',
            message='Your order #42 has been confirmed.',
        )

    def test_notification_str(self):
        self.assertIn('Order Confirmed', str(self.notification))

    def test_notification_default_read(self):
        self.assertFalse(self.notification.is_read)

    def test_notification_order(self):
        n1 = Notification.objects.create(
            user_id=1, type='welcome', title='Welcome', message='Hi!'
        )
        n2 = Notification.objects.create(
            user_id=1, type='promotional', title='Sale', message='50% off!'
        )
        latest = Notification.objects.filter(user_id=1).first()
        self.assertEqual(latest.id, n2.id)


class NotificationServiceTest(TestCase):
    def test_create_notification(self):
        from notifications.services.notification_service import create_notification
        n = create_notification(
            user_id=1,
            type='welcome',
            title='Welcome!',
            message='Thanks for joining.',
        )
        self.assertTrue(Notification.objects.filter(id=n.id).exists())

    def test_create_invalid_type(self):
        from notifications.services.notification_service import create_notification
        from shared.common.exceptions import BadRequestError
        with self.assertRaises(BadRequestError):
            create_notification(
                user_id=1, type='invalid', title='X', message='Y'
            )

    def test_mark_as_read(self):
        from notifications.services.notification_service import mark_as_read
        n = mark_as_read(self.notification.id, user_id=1)
        self.assertTrue(n.is_read)
        self.assertIsNotNone(n.read_at)

    def test_mark_all_as_read(self):
        from notifications.services.notification_service import mark_all_as_read
        Notification.objects.create(
            user_id=5, type='welcome', title='A', message='B'
        )
        Notification.objects.create(
            user_id=5, type='welcome', title='C', message='D'
        )
        count = mark_all_as_read(5)
        self.assertEqual(count, 2)
        self.assertFalse(
            Notification.objects.filter(user_id=5, is_read=False).exists()
        )

    def test_send_order_notification(self):
        from notifications.services.notification_service import send_order_notification
        n = send_order_notification(order_id=99, user_id=1, order_status='shipped')
        self.assertEqual(n.type, Notification.TYPE_ORDER_SHIPPED)
        self.assertIn('#99', n.message)


class NotificationSelectorTest(TestCase):
    def setUp(self):
        Notification.objects.create(
            user_id=7, type='welcome', title='A', message='B'
        )
        Notification.objects.create(
            user_id=7, type='welcome', title='C', message='D', is_read=True
        )

    def test_list_notifications(self):
        from notifications.selectors.notification_selector import list_user_notifications
        result = list_user_notifications(7)
        self.assertEqual(result.count(), 2)

    def test_list_unread_only(self):
        from notifications.selectors.notification_selector import list_user_notifications
        result = list_user_notifications(7, unread_only=True)
        self.assertEqual(result.count(), 1)

    def test_unread_count(self):
        from notifications.selectors.notification_selector import get_unread_count
        self.assertEqual(get_unread_count(7), 1)

    def test_notification_not_found(self):
        from notifications.selectors.notification_selector import get_notification_by_id
        from shared.common.exceptions import NotFoundError
        with self.assertRaises(NotFoundError):
            get_notification_by_id(99999)
