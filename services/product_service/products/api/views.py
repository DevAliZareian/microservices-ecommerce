from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from shared.common.permissions import IsServiceAccount
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from products.api.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    CategorySerializer,
    ReviewSerializer,
    ReviewCreateSerializer,
)
from products.api.filters import ProductFilter
from products.selectors.product_selector import (
    list_active_products,
    get_product_by_slug,
    get_product_by_id,
    list_featured_products,
    list_categories,
    get_product_reviews,
)
from products.services.product_service import update_stock, create_review
from shared.common.pagination import StandardPagination
from shared.common.responses import success_response, error_response


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filterset = ProductFilter(
            data=request.query_params,
            queryset=list_active_products(),
        )
        queryset = filterset.qs

        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        ordering = request.query_params.get('ordering', '-created_at')
        if ordering.lstrip('-') in ('price', 'created_at', 'name'):
            queryset = queryset.order_by(ordering)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = get_product_by_slug(slug)
        serializer = ProductDetailSerializer(product, context={'request': request})
        return success_response(data=serializer.data)


class ProductDetailByIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        product = get_product_by_id(product_id)
        serializer = ProductDetailSerializer(product, context={'request': request})
        return success_response(data=serializer.data)


class FeaturedProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = list_featured_products()
        serializer = ProductListSerializer(products, many=True)
        return success_response(data=serializer.data)


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = list_categories()
        serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)


class ProductManagementView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)
        product = serializer.save()
        return success_response(
            data=ProductDetailSerializer(product).data,
            http_status=status.HTTP_201_CREATED,
        )

    def put(self, request, product_id):
        product = get_product_by_id(product_id)
        serializer = ProductCreateUpdateSerializer(
            product, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)
        product = serializer.save()
        return success_response(data=ProductDetailSerializer(product).data)


class StockUpdateView(APIView):
    permission_classes = [IsServiceAccount]
    service_key = 'internal-service-key'

    def post(self, request, product_id):
        quantity_change = request.data.get('quantity_change', 0)
        try:
            product = update_stock(product_id, quantity_change)
            return success_response(
                data={'product_id': product.id, 'new_stock': product.stock_quantity}
            )
        except Exception as e:
            return error_response(errors=str(e), http_status=400)


class ReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        reviews = get_product_reviews(product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return success_response(data=serializer.data)


class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
        review = create_review(
            product_id=serializer.validated_data['product'].id,
            user_id=user_id,
            rating=serializer.validated_data['rating'],
            title=serializer.validated_data['title'],
            comment=serializer.validated_data['comment'],
        )
        return success_response(
            data=ReviewSerializer(review).data,
            http_status=status.HTTP_201_CREATED,
        )
