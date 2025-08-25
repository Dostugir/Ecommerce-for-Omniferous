from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create sample data for the e-commerce site'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Latest electronic gadgets and devices'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Fashionable clothing for all ages'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books for all interests and ages'},
            {'name': 'Home & Garden', 'slug': 'home-garden', 'description': 'Everything for your home and garden'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports equipment and accessories'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create products
        products_data = [
            # Electronics
            {
                'name': 'Smartphone X1',
                'slug': 'smartphone-x1',
                'description': 'Latest smartphone with advanced features and high-quality camera.',
                'price': Decimal('599.99'),
                'category': categories[0],
                'stock': 50,
                'featured': True
            },
            {
                'name': 'Laptop Pro',
                'slug': 'laptop-pro',
                'description': 'Professional laptop for work and gaming with high performance.',
                'price': Decimal('1299.99'),
                'sale_price': Decimal('1099.99'),
                'category': categories[0],
                'stock': 25,
                'featured': True
            },
            {
                'name': 'Wireless Headphones',
                'slug': 'wireless-headphones',
                'description': 'Premium wireless headphones with noise cancellation.',
                'price': Decimal('199.99'),
                'category': categories[0],
                'stock': 100
            },
            # Clothing
            {
                'name': 'Classic T-Shirt',
                'slug': 'classic-t-shirt',
                'description': 'Comfortable cotton t-shirt available in multiple colors.',
                'price': Decimal('24.99'),
                'category': categories[1],
                'stock': 200
            },
            {
                'name': 'Denim Jeans',
                'slug': 'denim-jeans',
                'description': 'High-quality denim jeans with perfect fit.',
                'price': Decimal('79.99'),
                'sale_price': Decimal('59.99'),
                'category': categories[1],
                'stock': 75
            },
            # Books
            {
                'name': 'Python Programming Guide',
                'slug': 'python-programming-guide',
                'description': 'Comprehensive guide to Python programming for beginners.',
                'price': Decimal('39.99'),
                'category': categories[2],
                'stock': 150
            },
            {
                'name': 'The Art of Cooking',
                'slug': 'art-of-cooking',
                'description': 'Beautiful cookbook with recipes from around the world.',
                'price': Decimal('49.99'),
                'category': categories[2],
                'stock': 80
            },
            # Home & Garden
            {
                'name': 'Garden Tool Set',
                'slug': 'garden-tool-set',
                'description': 'Complete set of essential garden tools for every gardener.',
                'price': Decimal('89.99'),
                'category': categories[3],
                'stock': 60
            },
            {
                'name': 'Coffee Maker',
                'slug': 'coffee-maker',
                'description': 'Automatic coffee maker for perfect coffee every time.',
                'price': Decimal('149.99'),
                'sale_price': Decimal('119.99'),
                'category': categories[3],
                'stock': 40,
                'featured': True
            },
            # Sports
            {
                'name': 'Yoga Mat',
                'slug': 'yoga-mat',
                'description': 'Premium yoga mat for comfortable practice.',
                'price': Decimal('34.99'),
                'category': categories[4],
                'stock': 120
            },
            {
                'name': 'Running Shoes',
                'slug': 'running-shoes',
                'description': 'Professional running shoes for maximum comfort and performance.',
                'price': Decimal('129.99'),
                'category': categories[4],
                'stock': 90
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
