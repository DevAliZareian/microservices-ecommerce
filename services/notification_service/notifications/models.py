from django.db import models


class Notification(models.Model):
    TYPE_ORDER_CONFIRMED = 'order_confirmed'
    TYPE_ORDER_SHIPPED = 'order_shipped'
    TYPE_ORDER_DELIVERED = 'order_delivered'
    TYPE_ORDER_CANCELLED = 'order_cancelled'
    TYPE_PAYMENT_RECEIVED = 'payment_received'
    TYPE_PAYMENT_FAILED = 'payment_failed'
    TYPE_WELCOME = 'welcome'
    TYPE_PROMOTIONAL = 'promotional'

    TYPE_CHOICES = [
        (TYPE_ORDER_CONFIRMED, 'Order Confirmed'),
        (TYPE_ORDER_SHIPPED, 'Order Shipped'),
        (TYPE_ORDER_DELIVERED, 'Order Delivered'),
        (TYPE_ORDER_CANCELLED, 'Order Cancelled'),
        (TYPE_PAYMENT_RECEIVED, 'Payment Received'),
        (TYPE_PAYMENT_FAILED, 'Payment Failed'),
        (TYPE_WELCOME, 'Welcome'),
        (TYPE_PROMOTIONAL, 'Promotional'),
    ]

    user_id = models.IntegerField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['is_read']),
            models.Index(fields=['user_id', 'is_read']),
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"