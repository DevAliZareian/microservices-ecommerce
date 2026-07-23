from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from shared.common.permissions import IsServiceAccount

from notifications.api.serializers import (
    NotificationSerializer, NotificationCreateSerializer,
)
from notifications.selectors.notification_selector import (
    list_user_notifications, get_unread_count, get_notification_by_id,
)
from notifications.services.notification_service import (
    create_notification, mark_as_read, mark_all_as_read,
    delete_notification, send_order_notification,
)
from shared.common.responses import success_response, error_response
from shared.common.exceptions import BadRequestError, NotFoundError


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_only = request.query_params.get('unread_only', '').lower() in ('true', '1')
        notifications = list_user_notifications(request.user.id, unread_only)
        serializer = NotificationSerializer(notifications, many=True)
        return success_response(data=serializer.data)


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = get_unread_count(request.user.id)
        return success_response(data={'count': count})


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, notification_id):
        try:
            notification = get_notification_by_id(notification_id, request.user.id)
            serializer = NotificationSerializer(notification)
            return success_response(data=serializer.data)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class MarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = mark_as_read(notification_id, request.user.id)
            serializer = NotificationSerializer(notification)
            return success_response(data=serializer.data)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = mark_all_as_read(request.user.id)
        return success_response(data={'marked_read': count})


class NotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, notification_id):
        try:
            delete_notification(notification_id, request.user.id)
            return success_response(data={'detail': 'Notification deleted.'})
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class AdminNotificationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = create_notification(**serializer.validated_data)
            data = NotificationSerializer(notification).data
            return success_response(data=data, http_status=status.HTTP_201_CREATED)
        except BadRequestError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_400_BAD_REQUEST)


class InternalOrderNotificationView(APIView):
    permission_classes = [IsServiceAccount]
    service_key = 'internal-service-key'

    def post(self, request):
        order_id = request.data.get('order_id')
        user_id = request.data.get('user_id')
        status = request.data.get('status')

        if not all([order_id, user_id, status]):
            return error_response(errors={'detail': 'order_id, user_id, and status are required.'},
                                  http_status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = send_order_notification(order_id, user_id, status)
            data = NotificationSerializer(notification).data
            return success_response(data=data, http_status=status.HTTP_201_CREATED)
        except BadRequestError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_400_BAD_REQUEST)