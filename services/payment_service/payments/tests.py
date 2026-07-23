from decimal import Decimal
from django.test import TestCase
from payments.models import Payment, Refund


class PaymentModelTest(TestCase):
    def setUp(self):
        self.payment = Payment.objects.create(
            order_id=1,
            user_id=1,
            amount=Decimal('99.99'),
            payment_method='credit_card',
            transaction_id='TXN-TEST123',
        )

    def test_payment_str(self):
        self.assertIn(str(self.payment.id), str(self.payment))

    def test_payment_default_status(self):
        self.assertEqual(self.payment.status, Payment.STATUS_PENDING)

    def test_payment_method_choices(self):
        self.assertEqual(self.payment.get_payment_method_display(), 'Credit Card')


class RefundModelTest(TestCase):
    def setUp(self):
        self.payment = Payment.objects.create(
            order_id=2,
            user_id=1,
            amount=Decimal('50.00'),
            payment_method='paypal',
            transaction_id='TXN-TEST456',
            status=Payment.STATUS_COMPLETED,
        )

    def test_full_refund(self):
        refund = Refund.objects.create(
            payment=self.payment,
            amount=Decimal('50.00'),
            reason='Customer request',
        )
        self.assertEqual(refund.payment, self.payment)
        self.assertEqual(self.payment.refunds.count(), 1)

    def test_partial_refund(self):
        Refund.objects.create(
            payment=self.payment,
            amount=Decimal('20.00'),
            reason='Partial issue',
        )
        total = sum(r.amount for r in self.payment.refunds.all())
        self.assertEqual(total, Decimal('20.00'))


class PaymentServiceTest(TestCase):
    def test_process_refund(self):
        from payments.services.payment_service import process_refund
        refund = process_refund(self.payment.id, reason='test')
        self.assertEqual(refund.amount, self.payment.amount)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_REFUNDED)

    def test_refund_not_completed_payment(self):
        from payments.services.payment_service import process_refund
        from shared.common.exceptions import BadRequestError
        with self.assertRaises(BadRequestError):
            process_refund(self.payment.id)

    def test_update_payment_status(self):
        from payments.services.payment_service import update_payment_status
        payment = Payment.objects.create(
            order_id=99, user_id=1, amount=Decimal('10.00'),
            payment_method='stripe', transaction_id='TXN-STATUS',
        )
        updated = update_payment_status(payment.id, 'processing')
        self.assertEqual(updated.status, 'processing')

    def test_invalid_status_transition(self):
        from payments.services.payment_service import update_payment_status
        from shared.common.exceptions import BadRequestError
        with self.assertRaises(BadRequestError):
            update_payment_status(self.payment.id, 'completed')


class PaymentSelectorTest(TestCase):
    def setUp(self):
        Payment.objects.create(
            order_id=10, user_id=5, amount=Decimal('25.00'),
            payment_method='credit_card', transaction_id='TXN-S1',
        )

    def test_get_by_id(self):
        from payments.selectors.payment_selector import get_payment_by_id
        p = Payment.objects.get(order_id=10)
        result = get_payment_by_id(p.id, user_id=5)
        self.assertEqual(result.order_id, 10)

    def test_get_by_order(self):
        from payments.selectors.payment_selector import get_payment_by_order
        result = get_payment_by_order(10, user_id=5)
        self.assertIsNotNone(result)

    def test_payment_not_found(self):
        from payments.selectors.payment_selector import get_payment_by_id
        from shared.common.exceptions import NotFoundError
        with self.assertRaises(NotFoundError):
            get_payment_by_id(99999)

    def test_list_user_payments(self):
        from payments.selectors.payment_selector import list_user_payments
        result = list_user_payments(5)
        self.assertEqual(result.count(), 1)
