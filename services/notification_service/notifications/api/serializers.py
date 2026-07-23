from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user_id', 'type', 'type_display', 'title',
            'message', 'is_read', 'link', 'created_at', 'read_at',
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'read_at']


class NotificationCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=Notification.TYPE_CHOICES)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    link = serializers.URLField(required=False, allow_blank=True)