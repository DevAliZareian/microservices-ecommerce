from django.db import models
from django.core.validators import MinValueValidator


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_PARTIALLY_REFUNDED = 'partially_refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
        (STATUS_PARTIALLY_REFUNDED, 'Partially Refunded'),
    ]

    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_DEBIT_CARD = 'debit_card'
    METHOD_PAYPAL = 'paypal'
    METHOD_STRIPE = 'stripe'
    METHOD_BANK_TRANSFER = 'bank_transfer'
    METHOD_CASH_ON_DELIVERY = 'cod'

    METHOD_CHOICES = [
        (METHOD_CREDIT_CARD, 'Credit Card'),
        (METHOD_DEBIT_CARD, 'Debit Card'),
        (METHOD_PAYPAL, 'PayPal'),
        (METHOD_STRIPE, 'Stripe'),
        (METHOD_BANK_TRANSFER, 'Bank Transfer'),
        (METHOD_CASH_ON_DELIVERY, 'Cash on Delivery'),
    ]

    order_id = models.IntegerField()
    user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(max_length=25, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    gateway_response = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order_id}"


class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.TextField()
    gateway_refund_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund #{self.id} for Payment #{self.payment_id}"