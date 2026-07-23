from decimal import Decimal
from django.test import TestCase
from orders.models import Order, OrderItem


class OrderModelTest(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            total=Decimal('59.98'),
            shipping_address={'street': '123 Main St', 'city': 'Testville'},
        )
        OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Widget',
            product_slug='widget',
            quantity=2,
            unit_price=Decimal('29.99'),
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f'Order #{self.order.id}')

    def test_order_items(self):
        self.assertEqual(self.order.items.count(), 1)

    def test_order_item_str(self):
        item = self.order.items.first()
        self.assertEqual(str(item), '2x Widget')

    def test_order_default_status(self):
        self.assertEqual(self.order.status, Order.STATUS_PENDING)

    def test_order_item_subtotal(self):
        item = self.order.items.first()
        self.assertEqual(item.subtotal, Decimal('59.98'))


class OrderStatusTest(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            total=Decimal('10.00'),
            shipping_address={'street': '123 Main St', 'city': 'Testville'},
        )

    def test_valid_transition(self):
        from orders.services.order_service import update_order_status
        order = update_order_status(self.order.id, 'confirmed', user_id=1)
        self.assertEqual(order.status, 'confirmed')

    def test_invalid_transition(self):
        from orders.services.order_service import update_order_status
        from shared.common.exceptions import BadRequestError
        with self.assertRaises(BadRequestError):
            update_order_status(self.order.id, 'shipped', user_id=1)

    def test_cancel_pending(self):
        from orders.services.order_service import cancel_order
        order = cancel_order(self.order.id, user_id=1)
        self.assertEqual(order.status, 'cancelled')


class OrderSelectorTest(TestCase):
    def setUp(self):
        Order.objects.create(
            user_id=10,
            total=Decimal('25.00'),
            shipping_address={'city': 'Test'},
        )
        Order.objects.create(
            user_id=10,
            total=Decimal('15.00'),
            status='confirmed',
            shipping_address={'city': 'Test'},
        )
        Order.objects.create(
            user_id=20,
            total=Decimal('50.00'),
            shipping_address={'city': 'Other'},
        )

    def test_list_user_orders(self):
        from orders.selectors.order_selector import list_user_orders
        result = list_user_orders(10)
        self.assertEqual(result.count(), 2)

    def test_list_user_orders_with_status(self):
        from orders.selectors.order_selector import list_user_orders
        result = list_user_orders(10, status='confirmed')
        self.assertEqual(result.count(), 1)

    def test_order_not_found(self):
        from orders.selectors.order_selector import get_order_by_id
        from shared.common.exceptions import NotFoundError
        with self.assertRaises(NotFoundError):
            get_order_by_id(99999)
