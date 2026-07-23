from rest_framework import serializers
from payments.models import Payment, Refund


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'payment', 'amount', 'reason', 'gateway_refund_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'user_id', 'amount', 'status', 'status_display',
            'payment_method', 'method_display', 'transaction_id',
            'gateway_response', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_id', 'transaction_id', 'created_at', 'updated_at']


class PaymentDetailSerializer(serializers.ModelSerializer):
    refunds = RefundSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'user_id', 'amount', 'status', 'status_display',
            'payment_method', 'method_display', 'transaction_id',
            'gateway_response', 'refunds', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)


class RefundCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reason = serializers.CharField(required=False, allow_blank=True)


class PaymentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES)