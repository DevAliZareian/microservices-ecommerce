from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/id/<int:product_id>/', views.ProductDetailByIdView.as_view(), name='product-detail-by-id'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('reviews/<int:product_id>/', views.ReviewListView.as_view(), name='review-list'),

    # Authenticated endpoints
    path('reviews/', views.ReviewCreateView.as_view(), name='review-create'),

    # Admin endpoints
    path('admin/products/', views.ProductManagementView.as_view(), name='product-create'),
    path('admin/products/<int:product_id>/', views.ProductManagementView.as_view(), name='product-update'),

    # Internal endpoints (for other services)
    path('internal/stock/<int:product_id>/', views.StockUpdateView.as_view(), name='stock-update'),
]