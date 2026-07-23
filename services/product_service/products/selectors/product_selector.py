from django.db.models import Avg, Count, Q
from products.models import Product, Category, ProductReview
from shared.common.exceptions import NotFoundError


def get_product_by_slug(slug: str) -> Product:
    try:
        return Product.objects.select_related('category').prefetch_related(
            'images'
        ).get(slug=slug, status='active')
    except Product.DoesNotExist:
        raise NotFoundError(f"Product with slug '{slug}' not found.")


def get_product_by_id(product_id: int) -> Product:
    try:
        return Product.objects.select_related('category').prefetch_related(
            'images'
        ).get(id=product_id)
    except Product.DoesNotExist:
        raise NotFoundError(f"Product with id {product_id} not found.")


def list_active_products(filters: dict = None):
    queryset = Product.objects.filter(
        status='active', stock_quantity__gt=0
    ).select_related('category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews'),
    )

    if filters:
        if 'category' in filters:
            queryset = queryset.filter(category__slug=filters['category'])
        if 'min_price' in filters:
            queryset = queryset.filter(price__gte=filters['min_price'])
        if 'max_price' in filters:
            queryset = queryset.filter(price__lte=filters['max_price'])
        if 'search' in filters:
            queryset = queryset.filter(
                Q(name__icontains=filters['search']) |
                Q(description__icontains=filters['search'])
            )

    return queryset


def list_featured_products():
    return Product.objects.filter(
        is_featured=True, status='active', stock_quantity__gt=0
    ).select_related('category')[:10]


def list_categories():
    return Category.objects.filter(
        is_active=True
    ).prefetch_related('subcategories')


def get_product_reviews(product_id: int):
    return ProductReview.objects.filter(
        product_id=product_id, is_approved=True
    ).order_by('-created_at')
