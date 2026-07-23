from payments.models import Payment, Refund
from shared.common.exceptions import NotFoundError


def get_payment_by_id(payment_id: int, user_id: int = None):
    try:
        if user_id:
            return Payment.objects.get(id=payment_id, user_id=user_id)
        return Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        raise NotFoundError(f"Payment with id {payment_id} not found.")


def get_payment_by_order(order_id: int, user_id: int = None):
    qs = Payment.objects.filter(order_id=order_id)
    if user_id:
        qs = qs.filter(user_id=user_id)
    payment = qs.first()
    if not payment:
        raise NotFoundError(f"No payment found for order {order_id}.")
    return payment


def list_user_payments(user_id: int, status: str = None):
    qs = Payment.objects.filter(user_id=user_id)
    if status:
        qs = qs.filter(status=status)
    return qs.order_by('-created_at')


def list_all_payments(status: str = None):
    qs = Payment.objects.all()
    if status:
        qs = qs.filter(status=status)
    return qs.order_by('-created_at')


def get_refunds_for_payment(payment_id: int):
    return Refund.objects.filter(payment_id=payment_id).order_by('-created_at')
