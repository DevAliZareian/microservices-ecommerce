from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/list/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),

    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:order_id>/', views.AdminOrderUpdateView.as_view(), name='admin-order-update'),
]