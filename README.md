# Django E-Commerce Webapp

A complete e-commerce web application built with Django framework featuring user authentication, product management, shopping cart, order processing, and payment integration.

## Features

- **User Authentication**: Register, login, logout, and profile management
- **Product Management**: Add, edit, delete products with categories
- **Shopping Cart**: Add/remove items, update quantities
- **Order Management**: Place orders, track order status
- **Payment Integration**: Stripe payment gateway
- **Admin Panel**: Full Django admin interface
- **Responsive Design**: Bootstrap-based responsive UI
- **Search Functionality**: Product search and filtering
- **User Reviews**: Product rating and review system

## Project Structure

```
ecommerce/
├── manage.py
├── requirements.txt
├── ecommerce/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── store/
│   └── accounts/
└── media/
    └── products/
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd ecommerce

# Or download and extract the project files
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6: Run the Development Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Configuration

### Environment Variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

### Stripe Payment Setup
1. Sign up for a Stripe account
2. Get your API keys from the Stripe dashboard
3. Add the keys to your `.env` file
4. For testing, use Stripe's test card numbers

## Usage Guide

### For Customers
1. **Browse Products**: Visit the homepage to see all products
2. **Search & Filter**: Use the search bar and category filters
3. **Add to Cart**: Click "Add to Cart" on any product
4. **Manage Cart**: View cart, update quantities, remove items
5. **Checkout**: Proceed to checkout and complete payment
6. **Track Orders**: View order history and status

### For Administrators
1. **Access Admin Panel**: Login at `/admin/`
2. **Manage Products**: Add, edit, delete products and categories
3. **Manage Orders**: View and update order status
4. **Manage Users**: View user accounts and profiles
5. **View Analytics**: Check sales and user statistics

## API Endpoints

- `GET /` - Homepage with products
- `GET /products/` - All products
- `GET /products/<id>/` - Product detail
- `GET /cart/` - Shopping cart
- `POST /cart/add/<id>/` - Add to cart
- `GET /checkout/` - Checkout page
- `POST /checkout/` - Process order
- `GET /orders/` - User orders
- `GET /accounts/login/` - Login page
- `GET /accounts/register/` - Registration page

## Customization

### Adding New Features
1. Create new models in `store/models.py`
2. Add views in `store/views.py`
3. Create templates in `templates/store/`
4. Update URLs in `store/urls.py`

### Styling
- CSS files are in `static/css/`
- Bootstrap 5 is included for responsive design
- Custom styles can be added to `style.css`

### Database
- Default: SQLite (for development)
- Production: PostgreSQL, MySQL, or other databases
- Update `settings.py` for database configuration

## Deployment

### Local Development
```bash
python manage.py runserver
```

### Production Deployment
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Use WSGI server (Gunicorn, uWSGI)
5. Deploy to platforms like Heroku, AWS, or DigitalOcean

## Security Features

- CSRF protection enabled
- SQL injection protection
- XSS protection
- Secure password hashing
- HTTPS enforcement (in production)

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test store
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the documentation
- Review the code comments
- Create an issue in the repository

## Future Enhancements

- Email notifications
- Advanced search filters
- Wishlist functionality
- Social media integration
- Mobile app
- Multi-language support
- Advanced analytics dashboard
