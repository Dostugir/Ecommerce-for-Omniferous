# Django E-Commerce Setup Guide

This guide will walk you through setting up the Django E-Commerce project step by step.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (optional, for version control)

## Quick Setup (Automated)

The easiest way to set up the project is using the automated setup script:

### 1. Run the Setup Script

```bash
python setup.py
```

This script will:
- Create a virtual environment
- Install all dependencies
- Set up the database
- Create a superuser account
- Generate sample data
- Configure the project

### 2. Start the Development Server

```bash
# Windows
venv\Scripts\activate
python manage.py runserver

# macOS/Linux
source venv/bin/activate
python manage.py runserver
```

### 3. Access Your E-Commerce Site

- **Main site**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/

## Manual Setup (Step by Step)

If you prefer to set up the project manually, follow these steps:

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Create a `.env` file in the project root:

```env
# Django E-Commerce Environment Variables
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
```

### Step 4: Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Run the Server

```bash
python manage.py runserver
```

## Configuration

### Stripe Payment Setup

1. **Sign up for Stripe**: Go to [stripe.com](https://stripe.com) and create an account
2. **Get API Keys**: 
   - Go to Dashboard → Developers → API Keys
   - Copy your Publishable Key and Secret Key
   - Update your `.env` file with these keys
3. **Test Cards**: Use these test card numbers for testing:
   - **Visa**: 4242 4242 4242 4242
   - **Mastercard**: 5555 5555 5555 4444
   - **Expiry**: Any future date
   - **CVC**: Any 3 digits

### Email Configuration

For production, configure email settings in your `.env` file:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Note**: For Gmail, you'll need to use an App Password, not your regular password.

## Project Structure

```
ecommerce/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── setup.py                 # Automated setup script
├── README.md                # Project documentation
├── SETUP_GUIDE.md           # This setup guide
├── .env                     # Environment variables (create this)
├── ecommerce/               # Main project directory
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── store/                   # Main app directory
│   ├── __init__.py
│   ├── admin.py             # Admin interface configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL patterns
│   └── forms.py             # Form definitions
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   └── store/               # Store app templates
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
└── media/                   # User-uploaded files
    ├── products/
    └── categories/
```

## Features Overview

### Customer Features
- **Product Browsing**: Browse products by category
- **Search & Filter**: Search products and filter by price, category
- **Shopping Cart**: Add/remove items, update quantities
- **User Registration**: Create account and manage profile
- **Order Management**: Place orders and track status
- **Product Reviews**: Rate and review products
- **Wishlist**: Save products for later

### Admin Features
- **Product Management**: Add, edit, delete products
- **Category Management**: Organize products by categories
- **Order Management**: View and update order status
- **User Management**: Manage customer accounts
- **Inventory Management**: Track stock levels
- **Sales Analytics**: View sales reports

### Technical Features
- **Responsive Design**: Works on all devices
- **Payment Integration**: Stripe payment processing
- **Security**: CSRF protection, secure authentication
- **Performance**: Optimized database queries
- **SEO Friendly**: Clean URLs and meta tags

## Usage Guide

### For Customers

1. **Browse Products**
   - Visit the homepage to see featured products
   - Use the search bar to find specific items
   - Filter by category, price, or sort options

2. **Add to Cart**
   - Click "Add to Cart" on any product
   - Adjust quantity if needed
   - View cart by clicking the cart icon

3. **Checkout**
   - Review cart items and total
   - Fill in shipping information
   - Complete payment with Stripe

4. **Track Orders**
   - View order history in your account
   - Check order status and tracking

### For Administrators

1. **Access Admin Panel**
   - Go to `/admin/` and login with superuser credentials
   - Manage all aspects of the store

2. **Add Products**
   - Go to Products → Add Product
   - Fill in product details and upload images
   - Set price, stock, and category

3. **Manage Orders**
   - View all orders in the Orders section
   - Update order status as items ship
   - Process refunds if needed

## Customization

### Adding New Features

1. **Create Models**: Add new models in `store/models.py`
2. **Create Views**: Add view functions in `store/views.py`
3. **Create Templates**: Add HTML templates in `templates/store/`
4. **Update URLs**: Add URL patterns in `store/urls.py`

### Styling

- **CSS**: Modify `static/css/style.css`
- **Bootstrap**: The project uses Bootstrap 5 for responsive design
- **Custom Styles**: Add your own CSS classes

### Database

- **Development**: Uses SQLite by default
- **Production**: Can be configured for PostgreSQL, MySQL, etc.
- **Migrations**: Run `python manage.py makemigrations` after model changes

## Deployment

### Local Development

```bash
python manage.py runserver
```

### Production Deployment

1. **Set Environment Variables**:
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ```

2. **Configure Database**:
   - Use PostgreSQL or MySQL for production
   - Update `DATABASE_URL` in settings

3. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

4. **WSGI Server**:
   - Use Gunicorn or uWSGI
   - Configure with Nginx or Apache

5. **Deployment Platforms**:
   - **Heroku**: Easy deployment with Git
   - **AWS**: Use Elastic Beanstalk or EC2
   - **DigitalOcean**: Deploy on Droplets
   - **Vercel**: Serverless deployment

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure virtual environment is activated
   - Check that all dependencies are installed

2. **Database Errors**
   - Run `python manage.py migrate`
   - Check database configuration

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings

4. **Payment Issues**
   - Verify Stripe API keys are correct
   - Check Stripe dashboard for errors
   - Use test cards for testing

5. **Image Upload Issues**
   - Check `MEDIA_URL` and `MEDIA_ROOT` settings
   - Ensure directory permissions are correct

### Getting Help

- Check the Django documentation: https://docs.djangoproject.com/
- Review the project's README.md file
- Check the console for error messages
- Verify all environment variables are set correctly

## Security Considerations

- **Change Default Secret Key**: Update `SECRET_KEY` in production
- **HTTPS**: Use HTTPS in production
- **Environment Variables**: Never commit sensitive data to version control
- **Database Security**: Use strong passwords and limit database access
- **Regular Updates**: Keep Django and dependencies updated

## Performance Optimization

- **Database Indexing**: Add indexes for frequently queried fields
- **Caching**: Implement Redis or Memcached for caching
- **CDN**: Use a CDN for static files
- **Image Optimization**: Compress product images
- **Database Queries**: Optimize database queries with `select_related` and `prefetch_related`

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the Django documentation
3. Check the project's GitHub issues (if available)
4. Create a detailed bug report with error messages

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Happy Coding! 🚀**

Your Django E-Commerce project is now ready to use. Start building your online store!
