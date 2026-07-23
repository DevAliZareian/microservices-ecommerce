from django.db import models
from django.core.validators import MinValueValidator

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(BaseModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price for displaying discounts"
    )

    # Inventory
    sku = models.CharField(max_length=50, unique=True)
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10)

    # Status & visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)

    # Relations
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )

    # Media
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)

    # SEO
    meta_title = models.CharField(max_length=120, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return round(discount, 2)
        return None


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(BaseModel):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user_id = models.IntegerField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user_id']

    def __str__(self):
        return f"{self.user_id}'s review of {self.product.name}"