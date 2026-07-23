from django.test import TestCase
from products.models import Category, Product, ProductReview


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices',
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Electronics')

    def test_subcategory(self):
        sub = Category.objects.create(
            name='Phones',
            slug='phones',
            parent=self.category,
        )
        self.assertEqual(sub.parent, self.category)
        self.assertIn(sub, self.category.subcategories.all())


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Books', slug='books'
        )
        self.product = Product.objects.create(
            name='Test Book',
            slug='test-book',
            description='A great book',
            price='19.99',
            sku='BOOK-001',
            stock_quantity=10,
            status='active',
            category=self.category,
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Book')

    def test_is_in_stock(self):
        self.assertTrue(self.product.is_in_stock)

    def test_is_not_in_stock(self):
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)

    def test_is_low_stock(self):
        self.product.stock_quantity = 5
        self.product.save()
        self.assertTrue(self.product.is_low_stock)

    def test_discount_percentage(self):
        self.product.compare_at_price = '29.99'
        self.product.save()
        self.assertIsNotNone(self.product.discount_percentage)
        self.assertAlmostEqual(self.product.discount_percentage, 33.33, places=1)

    def test_no_discount(self):
        self.assertIsNone(self.product.discount_percentage)


class ProductSelectorTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Gadgets', slug='gadgets'
        )
        self.product = Product.objects.create(
            name='Gadget Pro',
            slug='gadget-pro',
            description='A cool gadget',
            price='49.99',
            sku='GAD-001',
            stock_quantity=5,
            status='active',
            category=self.category,
        )

    def test_get_by_slug(self):
        from products.selectors.product_selector import get_product_by_slug
        result = get_product_by_slug('gadget-pro')
        self.assertEqual(result.name, 'Gadget Pro')

    def test_get_by_id(self):
        from products.selectors.product_selector import get_product_by_id
        result = get_product_by_id(self.product.id)
        self.assertEqual(result.slug, 'gadget-pro')

    def test_list_active_products(self):
        from products.selectors.product_selector import list_active_products
        result = list_active_products()
        self.assertIn(self.product, result)

    def test_product_not_found(self):
        from products.selectors.product_selector import get_product_by_slug
        from shared.common.exceptions import NotFoundError
        with self.assertRaises(NotFoundError):
            get_product_by_slug('nonexistent')


class ProductFilterTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Food', slug='food'
        )
        Product.objects.create(
            name='Chips', slug='chips', description='Tasty',
            price='3.99', sku='F-001', stock_quantity=50,
            status='active', category=self.category,
        )
        Product.objects.create(
            name='Steak', slug='steak', description='Premium',
            price='29.99', sku='F-002', stock_quantity=0,
            status='active', category=self.category,
        )

    def test_filter_by_price(self):
        from products.api.filters import ProductFilter
        qs = Product.objects.filter(status='active')
        fs = ProductFilter(data={'max_price': '10.00'}, queryset=qs)
        self.assertEqual(fs.qs.count(), 1)
        self.assertEqual(fs.qs.first().name, 'Chips')

    def test_filter_by_category(self):
        from products.api.filters import ProductFilter
        qs = Product.objects.filter(status='active')
        fs = ProductFilter(data={'category': 'food'}, queryset=qs)
        self.assertEqual(fs.qs.count(), 2)
