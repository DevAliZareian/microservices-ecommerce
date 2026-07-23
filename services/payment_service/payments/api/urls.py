from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payments/list/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:payment_id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/by-order/<int:order_id>/', views.PaymentByOrderView.as_view(), name='payment-by-order'),

    path('admin/payments/', views.AdminPaymentListView.as_view(), name='admin-payment-list'),
    path('admin/payments/<int:payment_id>/', views.AdminPaymentUpdateView.as_view(), name='admin-payment-update'),
    path('admin/payments/<int:payment_id>/refunds/', views.AdminRefundListView.as_view(), name='admin-refund-list'),
    path('admin/payments/<int:payment_id>/refund/', views.RefundCreateView.as_view(), name='refund-create'),
]