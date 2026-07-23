from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from orders.api.serializers import (
    OrderCreateSerializer, OrderListSerializer, OrderDetailSerializer,
    OrderStatusUpdateSerializer,
)
from orders.selectors.order_selector import (
    get_order_by_id, list_user_orders, list_all_orders,
)
from orders.services.order_service import create_order, update_order_status
from shared.common.responses import success_response, error_response
from shared.common.exceptions import BadRequestError, NotFoundError


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

        try:
            order = create_order(
                user_id=request.user.id,
                items=serializer.validated_data['items'],
                shipping_address=serializer.validated_data['shipping_address'],
                billing_address=serializer.validated_data.get('billing_address'),
                notes=serializer.validated_data.get('notes', ''),
            )
            data = OrderDetailSerializer(order).data
            return success_response(data=data, http_status=status.HTTP_201_CREATED)
        except BadRequestError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_400_BAD_REQUEST)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get('status')
        orders = list_user_orders(request.user.id, status_filter)
        serializer = OrderListSerializer(orders, many=True)
        return success_response(data=serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = get_order_by_id(order_id, request.user.id)
            serializer = OrderDetailSerializer(order)
            return success_response(data=serializer.data)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = update_order_status(order_id, 'cancelled', request.user.id)
            serializer = OrderDetailSerializer(order)
            return success_response(data=serializer.data)
        except (BadRequestError, NotFoundError) as e:
            return error_response(errors={'detail': str(e)},
                                  http_status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))


class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        status_filter = request.query_params.get('status')
        orders = list_all_orders(status_filter)
        serializer = OrderListSerializer(orders, many=True)
        return success_response(data=serializer.data)


class AdminOrderUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, order_id):
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

        try:
            order = update_order_status(order_id, serializer.validated_data['status'])
            data = OrderDetailSerializer(order).data
            return success_response(data=data)
        except BadRequestError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_400_BAD_REQUEST)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)