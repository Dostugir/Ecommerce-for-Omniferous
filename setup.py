#!/usr/bin/env python3
"""
Setup script for Django E-Commerce Project
This script automates the initial setup process.
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Django E-Commerce Environment Variables
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Stripe Settings (Get these from https://dashboard.stripe.com/apikeys)
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here

# Email Settings (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
        print("⚠️  Please update the .env file with your actual settings")
    else:
        print("ℹ️  .env file already exists")

def create_sample_data():
    """Create sample categories and products"""
    print("\n🔄 Creating sample data...")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    django.setup()
    
    from store.models import Category, Product
    from django.core.files.base import ContentFile
    from PIL import Image
    import io
    
    # Create sample categories
    categories_data = [
        {
            'name': 'Electronics',
            'slug': 'electronics',
            'description': 'Latest electronic gadgets and devices'
        },
        {
            'name': 'Clothing',
            'slug': 'clothing',
            'description': 'Fashion and apparel for all ages'
        },
        {
            'name': 'Books',
            'slug': 'books',
            'description': 'Books, magazines, and educational materials'
        },
        {
            'name': 'Home & Garden',
            'slug': 'home-garden',
            'description': 'Home improvement and garden supplies'
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"✅ Created category: {category.name}")
    
    # Create sample products
    products_data = [
        {
            'name': 'Wireless Bluetooth Headphones',
            'slug': 'wireless-bluetooth-headphones',
            'description': 'High-quality wireless headphones with noise cancellation',
            'price': 99.99,
            'sale_price': 79.99,
            'stock': 50,
            'category': categories[0],
            'featured': True
        },
        {
            'name': 'Smartphone Case',
            'slug': 'smartphone-case',
            'description': 'Durable protective case for smartphones',
            'price': 29.99,
            'stock': 100,
            'category': categories[0]
        },
        {
            'name': 'Cotton T-Shirt',
            'slug': 'cotton-t-shirt',
            'description': 'Comfortable cotton t-shirt in various colors',
            'price': 19.99,
            'sale_price': 15.99,
            'stock': 200,
            'category': categories[1],
            'featured': True
        },
        {
            'name': 'Programming Book',
            'slug': 'programming-book',
            'description': 'Comprehensive guide to modern programming',
            'price': 49.99,
            'stock': 25,
            'category': categories[2]
        },
        {
            'name': 'Garden Tool Set',
            'slug': 'garden-tool-set',
            'description': 'Complete set of essential garden tools',
            'price': 89.99,
            'sale_price': 69.99,
            'stock': 30,
            'category': categories[3]
        }
    ]
    
    # Create a simple placeholder image
    def create_placeholder_image():
        img = Image.new('RGB', (300, 300), color='#f0f0f0')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return ContentFile(img_io.getvalue(), 'placeholder.jpg')
    
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            slug=prod_data['slug'],
            defaults=prod_data
        )
        if created:
            # Add placeholder image
            product.image.save('placeholder.jpg', create_placeholder_image(), save=True)
            print(f"✅ Created product: {product.name}")
    
    print("✅ Sample data creation completed")

def main():
    """Main setup function"""
    print("🚀 Django E-Commerce Setup Script")
    print("=" * 50)
    
    # Check if Python and pip are available
    if not run_command("python --version", "Checking Python version"):
        print("❌ Python is not available. Please install Python 3.8+")
        return
    
    # Create virtual environment
    if not os.path.exists('venv'):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return
    else:
        print("ℹ️  Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return
    
    # Create .env file
    create_env_file()
    
    # Run Django migrations
    if not run_command(f"{activate_cmd} && python manage.py makemigrations", "Creating database migrations"):
        return
    
    if not run_command(f"{activate_cmd} && python manage.py migrate", "Applying database migrations"):
        return
    
    # Create superuser
    print("\n🔄 Creating superuser...")
    print("Please enter the following information for the admin user:")
    superuser_cmd = f"{activate_cmd} && python manage.py createsuperuser"
    try:
        subprocess.run(superuser_cmd, shell=True, check=True)
        print("✅ Superuser created successfully")
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation was cancelled or failed")
    
    # Create sample data
    try:
        create_sample_data()
    except Exception as e:
        print(f"⚠️  Sample data creation failed: {e}")
        print("You can create sample data manually through the admin panel")
    
    # Collect static files
    if not run_command(f"{activate_cmd} && python manage.py collectstatic --noinput", "Collecting static files"):
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your actual settings")
    print("2. Get Stripe API keys from https://dashboard.stripe.com/apikeys")
    print("3. Run the development server: python manage.py runserver")
    print("4. Visit http://127.0.0.1:8000/ to see your e-commerce site")
    print("5. Visit http://127.0.0.1:8000/admin/ to manage your store")
    
    print("\n🔧 To start the development server:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    print("   python manage.py runserver")

if __name__ == "__main__":
    main()
