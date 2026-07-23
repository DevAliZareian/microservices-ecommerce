from decimal import Decimal
import uuid
from django.conf import settings
from payments.models import Payment, Refund
from payments.selectors.payment_selector import get_payment_by_id
from shared.common.client import ServiceClient
from shared.common.exceptions import BadRequestError

_order_client = ServiceClient(
    base_url=settings.ORDER_SERVICE_URL,
    service_key=settings.SERVICE_KEY,
)


def _generate_transaction_id():
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def _get_order_total(order_id: int) -> Decimal:
    resp = _order_client.get(f'/api/v1/orders/{order_id}/')
    data = resp.get('data', {})
    return Decimal(str(data.get('total', '0')))


def process_payment(order_id: int, user_id: int, payment_method: str):
    existing = Payment.objects.filter(order_id=order_id).first()
    if existing and existing.status in (
        Payment.STATUS_COMPLETED, Payment.STATUS_PROCESSING
    ):
        raise BadRequestError("Payment already exists for this order.")

    total = _get_order_total(order_id)

    payment = Payment.objects.create(
        order_id=order_id,
        user_id=user_id,
        amount=total,
        payment_method=payment_method,
        transaction_id=_generate_transaction_id(),
        status=Payment.STATUS_PROCESSING,
    )

    try:
        payment.status = Payment.STATUS_COMPLETED
        payment.save()
    except Exception:
        payment.status = Payment.STATUS_FAILED
        payment.gateway_response = {'error': 'Payment gateway error'}
        payment.save()

    return payment


def process_refund(payment_id: int, amount: Decimal = None, reason: str = ''):
    payment = get_payment_by_id(payment_id)

    if payment.status not in (
        Payment.STATUS_COMPLETED, Payment.STATUS_PARTIALLY_REFUNDED
    ):
        raise BadRequestError("Payment must be completed before refund.")

    refund_amount = amount or payment.amount
    if refund_amount > payment.amount:
        raise BadRequestError("Refund amount exceeds payment amount.")

    refund = Refund.objects.create(
        payment=payment,
        amount=refund_amount,
        reason=reason,
        gateway_refund_id=f"REF-{uuid.uuid4().hex[:12].upper()}",
    )

    total_refunded = (
        sum(r.amount for r in payment.refunds.all()) + refund_amount
    )
    if total_refunded >= payment.amount:
        payment.status = Payment.STATUS_REFUNDED
    else:
        payment.status = Payment.STATUS_PARTIALLY_REFUNDED
    payment.save()

    return refund


def update_payment_status(payment_id: int, new_status: str):
    payment = get_payment_by_id(payment_id)

    valid_transitions = {
        Payment.STATUS_PENDING: [Payment.STATUS_PROCESSING, Payment.STATUS_FAILED],
        Payment.STATUS_PROCESSING: [Payment.STATUS_COMPLETED, Payment.STATUS_FAILED],
        Payment.STATUS_COMPLETED: [
            Payment.STATUS_REFUNDED, Payment.STATUS_PARTIALLY_REFUNDED,
        ],
        Payment.STATUS_FAILED: [Payment.STATUS_PENDING],
        Payment.STATUS_REFUNDED: [],
        Payment.STATUS_PARTIALLY_REFUNDED: [Payment.STATUS_REFUNDED],
    }

    allowed = valid_transitions.get(payment.status, [])
    if new_status not in allowed:
        raise BadRequestError(
            f"Cannot transition from '{payment.status}' to '{new_status}'."
        )

    payment.status = new_status
    payment.save()
    return payment
