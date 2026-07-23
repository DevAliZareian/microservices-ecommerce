from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from payments.api.serializers import (
    PaymentSerializer, PaymentDetailSerializer, PaymentCreateSerializer,
    RefundSerializer, RefundCreateSerializer, PaymentStatusUpdateSerializer,
)
from payments.selectors.payment_selector import (
    get_payment_by_id, get_payment_by_order, list_user_payments,
    list_all_payments, get_refunds_for_payment,
)
from payments.services.payment_service import (
    process_payment, process_refund, update_payment_status,
)
from shared.common.responses import success_response, error_response
from shared.common.exceptions import BadRequestError, NotFoundError


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = process_payment(
                order_id=serializer.validated_data['order_id'],
                user_id=request.user.id,
                payment_method=serializer.validated_data['payment_method'],
            )
            data = PaymentSerializer(payment).data
            return success_response(data=data, http_status=status.HTTP_201_CREATED)
        except BadRequestError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get('status')
        payments = list_user_payments(request.user.id, status_filter)
        serializer = PaymentSerializer(payments, many=True)
        return success_response(data=serializer.data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = get_payment_by_id(payment_id, request.user.id)
            serializer = PaymentDetailSerializer(payment)
            return success_response(data=serializer.data)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class PaymentByOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            payment = get_payment_by_order(order_id, request.user.id)
            serializer = PaymentDetailSerializer(payment)
            return success_response(data=serializer.data)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class RefundCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, payment_id):
        serializer = RefundCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

        try:
            refund = process_refund(
                payment_id=payment_id,
                amount=serializer.validated_data.get('amount'),
                reason=serializer.validated_data.get('reason', ''),
            )
            data = RefundSerializer(refund).data
            return success_response(data=data, http_status=status.HTTP_201_CREATED)
        except (BadRequestError, NotFoundError) as e:
            return error_response(errors={'detail': str(e)},
                                  http_status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))


class AdminPaymentListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        status_filter = request.query_params.get('status')
        payments = list_all_payments(status_filter)
        serializer = PaymentSerializer(payments, many=True)
        return success_response(data=serializer.data)


class AdminPaymentUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, payment_id):
        serializer = PaymentStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = update_payment_status(payment_id, serializer.validated_data['status'])
            data = PaymentDetailSerializer(payment).data
            return success_response(data=data)
        except BadRequestError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_400_BAD_REQUEST)
        except NotFoundError as e:
            return error_response(errors={'detail': str(e)}, http_status=status.HTTP_404_NOT_FOUND)


class AdminRefundListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, payment_id):
        refunds = get_refunds_for_payment(payment_id)
        serializer = RefundSerializer(refunds, many=True)
        return success_response(data=serializer.data)