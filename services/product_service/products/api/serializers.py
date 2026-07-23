from rest_framework import serializers
from products.models import Product, Category, ProductImage, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'image', 'subcategories', 'product_count'
        ]

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing products."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price',
            'compare_at_price', 'discount_percentage', 'main_image',
            'is_in_stock', 'is_featured', 'avg_rating', 'review_count',
            'category_name', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product detail including images and reviews."""
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'compare_at_price', 'discount_percentage', 'sku',
            'stock_quantity', 'is_in_stock', 'is_low_stock', 'is_featured',
            'status', 'category', 'main_image', 'images',
            'avg_rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'updated_at'
        ]

    def get_avg_rating(self, obj):
        from django.db.models import Avg
        result = obj.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'))
        return result['avg']

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin product management."""
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'short_description',
            'price', 'compare_at_price', 'sku', 'stock_quantity',
            'low_stock_threshold', 'status', 'is_featured',
            'category', 'main_image', 'meta_title', 'meta_description'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user_id', 'rating', 'title', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['product', 'rating', 'title', 'comment']