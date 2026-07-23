from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/unread-count/', views.UnreadCountView.as_view(), name='unread-count'),
    path('notifications/<int:notification_id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:notification_id>/read/', views.MarkReadView.as_view(), name='mark-read'),
    path('notifications/read-all/', views.MarkAllReadView.as_view(), name='mark-all-read'),
    path('notifications/<int:notification_id>/delete/', views.NotificationDeleteView.as_view(), name='notification-delete'),

    path('admin/notifications/', views.AdminNotificationCreateView.as_view(), name='admin-notification-create'),

    path('internal/order-notification/', views.InternalOrderNotificationView.as_view(), name='order-notification'),
]