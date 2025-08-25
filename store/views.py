from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
import stripe
import json

from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem, 
    Review, Wishlist
)
from .forms import ReviewForm, CheckoutForm, ProductSearchForm, UserRegistrationForm

# Initialize Stripe
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
except AttributeError:
    stripe.api_key = 'sk_test_your_stripe_secret_key'


def home(request):
    """Homepage with featured products and categories"""
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    categories = Category.objects.all()[:6]
    latest_products = Product.objects.filter(available=True).order_by('-created_at')[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'latest_products': latest_products,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """Product listing page with search and filtering"""
    products = Product.objects.filter(available=True)
    form = ProductSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        if category:
            products = products.filter(category__slug=category)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
        
        if sort_by:
            products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail page with reviews"""
    product = get_object_or_404(Product, slug=slug, available=True)
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has already reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been added!')
            return redirect('product_detail', slug=slug)
    else:
        review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_review': user_review,
        'review_form': review_form,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def category_detail(request, slug):
    """Category detail page"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
    }
    return render(request, 'store/category_detail.html', context)


def get_or_create_cart(request):
    """Helper function to get or create cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


def cart_detail(request):
    """Shopping cart page"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, 'Not enough stock available!')
        return redirect('store:product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    
    cart_item.save()
    messages.success(request, f'{product.name} added to cart!')
    
    return redirect('store:cart_detail')


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
    elif quantity > cart_item.product.stock:
        messages.error(request, 'Not enough stock available!')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated!')
    
    return redirect('store:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('store:cart_detail')


@login_required
def checkout(request):
    """Checkout page"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('store:product_list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.get_total_price()
            order.payment_method = 'stripe'
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.get_price()
                )
            
            # Clear cart
            cart.delete()
            
            # Redirect to payment
            return redirect('store:payment', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'store/checkout.html', context)


@login_required
@csrf_exempt
def payment(request, order_id):
    """Payment processing page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={'order_id': order.id}
            )
            
            order.stripe_payment_intent = intent.id
            order.save()
            
            return JsonResponse({
                'client_secret': intent.client_secret
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'store/payment.html', context)


@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.payment_status = 'paid'
    order.status = 'processing'
    order.save()
    
    messages.success(request, f'Payment successful! Order #{order.order_number}')
    return render(request, 'store/payment_success.html', {'order': order})


@login_required
def order_list(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('store:home')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'store/register.html', context)


@login_required
def wishlist(request):
    """User's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    
    return redirect('store:product_detail', slug=product.slug)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    messages.success(request, 'Item removed from wishlist!')
    return redirect('store:wishlist')


def search_products(request):
    """AJAX search for products"""
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            available=True
        )[:5]
        results = [{
            'id': product.id,
            'name': product.name,
            'price': str(product.get_price()),
            'url': product.get_absolute_url(),
            'image': product.image.url if product.image else '',
        } for product in products]
    else:
        results = []
    
    return JsonResponse({'results': results})
