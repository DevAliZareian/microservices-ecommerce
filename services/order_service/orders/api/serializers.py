from rest_framework import serializers
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_slug',
            'quantity', 'unit_price', 'subtotal',
        ]
        read_only_fields = ['id', 'product_name', 'product_slug', 'subtotal']


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True, min_length=1)
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user_id', 'status', 'total',
            'item_count', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user_id', 'status', 'total',
            'shipping_address', 'billing_address', 'notes',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)