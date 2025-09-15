from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .decorators import delivery_man_required, staff_required # Import the new decorator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, Exists, OuterRef # Import Exists and OuterRef
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
import stripe
import json
from django.utils import timezone # Import timezone for flash sales
from django import forms # Import forms for OrderStatusUpdateForm

from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem, 
    Review, Wishlist, Ad, FlashSaleCampaign, FlashSaleItem, DeliveryMan # Add new models
)
from .forms import ReviewForm, CheckoutForm, ProductSearchForm, UserRegistrationForm, AssignDeliveryForm, UserProfileForm, CustomPasswordChangeForm # Add new forms

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

    if request.user.is_authenticated:
        wishlist_subquery = Wishlist.objects.filter(user=request.user, product=OuterRef('pk'))
        featured_products = featured_products.annotate(is_in_wishlist=Exists(wishlist_subquery))
        latest_products = latest_products.annotate(is_in_wishlist=Exists(wishlist_subquery))

    # Fetch active ads
    active_ads = Ad.objects.filter(is_active=True).order_by('-created_at')

    # Fetch active flash sale campaign and its items
    active_flash_sale = FlashSaleCampaign.objects.filter(
        is_active=True, 
        start_date__lte=timezone.now(), 
        end_date__gte=timezone.now()
    ).first()

    flash_sale_items = []
    if active_flash_sale:
        flash_sale_items = FlashSaleItem.objects.filter(
            campaign=active_flash_sale, 
            quantity_available__gt=0,
            product__available=True
        ).order_by('product__name')[:8] # Limit to 8 items for display
        
        if request.user.is_authenticated:
            # Annotate flash_sale_items' products with whether they are in the current user's wishlist
            wishlist_subquery = Wishlist.objects.filter(user=request.user, product=OuterRef('product__pk'))
            flash_sale_items = flash_sale_items.annotate(product__is_in_wishlist=Exists(wishlist_subquery))
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'latest_products': latest_products,
        'active_ads': active_ads, # Add active ads to context
        'active_flash_sale': active_flash_sale, # Add active flash sale campaign
        'flash_sale_items': flash_sale_items, # Add flash sale items
    }
    return render(request, 'store/home.html', context)


def flash_sale_list(request):
    """Display all active flash sale products"""
    active_flash_sale = FlashSaleCampaign.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()

    flash_sale_items = []
    if active_flash_sale:
        flash_sale_items = FlashSaleItem.objects.filter(
            campaign=active_flash_sale,
            quantity_available__gt=0,
            product__available=True
        ).order_by('product__name')
        
        if request.user.is_authenticated:
            # Annotate flash_sale_items' products with whether they are in the current user's wishlist
            wishlist_subquery = Wishlist.objects.filter(user=request.user, product=OuterRef('product__pk'))
            flash_sale_items = flash_sale_items.annotate(product__is_in_wishlist=Exists(wishlist_subquery))

    paginator = Paginator(flash_sale_items, 12)  # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'active_flash_sale': active_flash_sale,
        'flash_sale_items': page_obj,
    }
    return render(request, 'store/flash_sale_list.html', context)


def product_list(request):
    """Product listing page with search and filtering"""
    products = Product.objects.filter(available=True)
    form = ProductSearchForm(request.GET)
    
    if request.user.is_authenticated:
        # Annotate products with whether they are in the current user's wishlist
        wishlist_subquery = Wishlist.objects.filter(user=request.user, product=OuterRef('pk'))
        products = products.annotate(is_in_wishlist=Exists(wishlist_subquery))

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
            # Filter by sale price if available, otherwise by regular price
            products = products.filter(
                Q(sale_price__isnull=False, sale_price__gte=min_price) |
                Q(sale_price__isnull=True, price__gte=min_price)
            )
        
        if max_price:
            # Filter by sale price if available, otherwise by regular price
            products = products.filter(
                Q(sale_price__isnull=False, sale_price__lte=max_price) |
                Q(sale_price__isnull=True, price__lte=max_price)
            )
        
        if sort_by:
            if sort_by in ['price', '-price']:
                # For price sorting, we need to use a custom ordering that considers sale price
                if sort_by == 'price':
                    # Order by sale price if available, otherwise by regular price (ascending)
                    products = products.extra(
                        select={'effective_price': 'COALESCE(sale_price, price)'}
                    ).order_by('effective_price')
                else:  # -price
                    # Order by sale price if available, otherwise by regular price (descending)
                    products = products.extra(
                        select={'effective_price': 'COALESCE(sale_price, price)'}
                    ).order_by('-effective_price')
            else:
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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If it's an AJAX request, render only the product grid partial
        rendered_html = render(request, 'store/_product_grid.html', context).content.decode('utf-8')
        return JsonResponse({'html': rendered_html, 'count': page_obj.paginator.count})

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
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    else:
        is_in_wishlist = False
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]

    # Collect IDs of products already displayed or excluded
    excluded_product_ids = [product.id]
    excluded_product_ids.extend(related_products.values_list('id', flat=True))

    # Trending categories and products
    trending_categories = Category.objects.annotate(product_count=Count('products'))\
                                          .order_by('-product_count')[:3]
    
    trending_products_list = []
    for category in trending_categories:
        # Fetch 2 products from each trending category, excluding already picked ones
        products_from_category = Product.objects.filter(
            category=category, available=True
        ).exclude(id__in=excluded_product_ids).order_by('?')[:2]
        for p in products_from_category:
            trending_products_list.append(p)
            excluded_product_ids.append(p.id) # Add to excluded list to avoid duplicates
    
    # If not enough trending products, fill with other available products randomly
    if len(trending_products_list) < 4:
        additional_products_needed = 4 - len(trending_products_list)
        additional_products = Product.objects.filter(available=True)\
                                     .exclude(id__in=excluded_product_ids).order_by('?')[:additional_products_needed]
        for p in additional_products:
            trending_products_list.append(p)
    
    # Convert the list back to a queryset for template consistency
    # This also handles the case where trending_products_list might be empty
    trending_products = Product.objects.filter(id__in=[p.id for p in trending_products_list])
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been added!')
            return redirect('store:product_detail', slug=slug)
    else:
        review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_review': user_review,
        'review_form': review_form,
        'related_products': related_products,
        'trending_products': trending_products, # Add trending products to context
        'is_in_wishlist': is_in_wishlist, # Add is_in_wishlist to context
    }
    return render(request, 'store/product_detail.html', context)


def category_detail(request, slug):
    """Category detail page"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)

    if request.user.is_authenticated:
        # Annotate products with whether they are in the current user's wishlist
        wishlist_subquery = Wishlist.objects.filter(user=request.user, product=OuterRef('pk'))
        products = products.annotate(is_in_wishlist=Exists(wishlist_subquery))
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If it's an AJAX request, render only the product grid partial
        rendered_html = render(request, 'store/_product_grid.html', context).content.decode('utf-8')
        return JsonResponse({'html': rendered_html, 'count': page_obj.paginator.count})

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
    try:
        cart = get_or_create_cart(request)
        cart_items = cart.items.all()
        
        # Get recommended products (exclude products already in cart)
        cart_product_ids = cart_items.values_list('product_id', flat=True)
        recommended_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids).order_by('?')[:4]
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'recommended_products': recommended_products,
        }
        return render(request, 'store/cart.html', context)
    except Exception as e:
        messages.error(request, f"Error loading cart: {str(e)}")
        return render(request, 'store/cart.html', {
            'cart': None,
            'cart_items': [],
            'recommended_products': [],
        })


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
    
    # Redirect back to the same page or product detail page
    redirect_to = request.META.get('HTTP_REFERER')
    if not redirect_to:
        redirect_to = redirect('store:product_detail', slug=product.slug).url
    return redirect(redirect_to)


@require_POST
def buy_now_direct(request, product_id):
    """Directly buy a product, bypassing the cart, and proceed to checkout."""
    product = get_object_or_404(Product, id=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        messages.error(request, 'Not enough stock available!')
        return redirect('store:product_detail', slug=product.slug)

    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to use the Buy Now option.')
        return redirect('account_login') # Redirect to login page if not logged in

    # Create a new, temporary order for this direct purchase
    # Do NOT add to the user's main cart
    order = Order.objects.create(
        user=request.user,
        total_amount=product.get_price() * quantity,
        payment_method='stripe', # Default payment method for now
        status='pending', # Initial status
        # Other fields like shipping address will be filled in checkout
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        price=product.get_price()
    )

    messages.success(request, f'Proceeding to checkout for {product.name}!')
    return redirect('store:checkout_with_order', order_id=order.id)


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to update your cart.')
        return redirect('store:cart_detail')
    
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Not enough stock available! Maximum: {cart_item.product.stock}')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
            
    except ValueError:
        messages.error(request, 'Invalid quantity provided.')
    except Exception as e:
        messages.error(request, 'Error updating cart. Please try again.')
    
    return redirect('store:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('store:cart_detail')


@login_required
def checkout(request, order_id=None):
    """Checkout page"""
    if order_id:
        order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
        order_items = order.items.all()
        total_amount = order.total_amount
        # No cart involved in direct buy, so cart_items will be order_items
        cart_items = order_items # For template compatibility
    else:
        cart = get_or_create_cart(request)
        cart_items = cart.items.all()
        total_amount = cart.get_total_price()
        order = None # No existing order if coming from cart

    if not cart_items:
        messages.warning(request, 'Your cart is empty or no products were selected for direct purchase!')
        return redirect('store:product_list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # If an order already exists (direct buy), update it
            if order_id:
                order.first_name = form.cleaned_data['first_name']
                order.last_name = form.cleaned_data['last_name']
                order.email = form.cleaned_data['email']
                order.address = form.cleaned_data['address']
                order.city = form.cleaned_data['city']
                order.country = form.cleaned_data['country']
                order.postal_code = form.cleaned_data['zip_code'] # Corrected to postal_code
                order.phone = form.cleaned_data['phone_number'] # Corrected to phone
                order.total_amount = total_amount # Ensure total amount is correct
                order.save()
                messages.success(request, 'Order details updated!')
            else: # Otherwise, create a new order from cart
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = total_amount
                order.payment_method = 'stripe' # Default to stripe
                order.status = 'pending'
                order.save()
                
                # Create order items from cart items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.get_price()
                    )
                # Clear cart only if it was a cart checkout
                cart.delete()
            
            # Redirect to payment with the order ID
            return redirect('store:payment', order_id=order.id)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        if order_id and order: # Pre-fill address if available in order for direct buy
            initial_data.update({
                'address': order.address,
                'city': order.city,
                'country': order.country,
                'zip_code': order.postal_code, # Corrected to postal_code
                'phone_number': order.phone, # Corrected to phone
            })
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items, # This will be order_items if direct buy
        'total_amount': total_amount,
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


@staff_required
def admin_assign_delivery(request, order_id):
    """Admin interface to assign a delivery man to an order"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = AssignDeliveryForm(request.POST)
        if form.is_valid():
            delivery_man = form.cleaned_data['delivery_man']
            order.assigned_to = delivery_man
            order.status = 'shipped' # Automatically set to 'shipped' when assigned
            order.save()
            messages.success(request, f"Order #{order.order_number} assigned to {delivery_man.user.username}.")
            return redirect('store:order_detail', order_id=order.id)
    else:
        form = AssignDeliveryForm()
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'store/admin_assign_delivery.html', context)


@delivery_man_required
def delivery_man_dashboard(request):
    """Delivery man dashboard to view assigned orders"""
    # Ensure the logged-in user is a delivery man
    try:
        delivery_man = request.user.delivery_profile
    except DeliveryMan.DoesNotExist:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('store:home') # Redirect to home or a suitable unauthorized page

    orders = Order.objects.filter(assigned_to=delivery_man).order_by('-created_at')

    context = {
        'delivery_man': delivery_man,
        'orders': orders,
        'STATUS_CHOICES': Order.STATUS_CHOICES,
    }
    response = render(request, 'store/delivery_man_dashboard.html', context)
    # Add cache control headers to prevent duplicate messages
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@delivery_man_required
@require_POST
def update_delivery_status(request, order_id):
    """API endpoint for delivery man to update order status"""
    try:
        delivery_man = request.user.delivery_profile
    except DeliveryMan.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    order = get_object_or_404(Order, id=order_id, assigned_to=delivery_man)
    new_status = request.POST.get('status')

    # Validate new_status against STATUS_CHOICES
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status and new_status in valid_statuses:
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.order_number} status updated to {new_status}.")
        return JsonResponse({'success': True, 'message': 'Status updated successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid status provided'}, status=400)


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    can_assign_delivery = request.user.is_staff # Only staff can assign
    is_assigned_delivery_man = False
    if request.user.is_authenticated and hasattr(request.user, 'delivery_profile'):
        is_assigned_delivery_man = (order.assigned_to == request.user.delivery_profile)
    
    assign_form = None
    status_form = None

    # Handle POST requests
    if request.method == 'POST':
        if can_assign_delivery and 'assign_delivery_man' in request.POST:
            assign_form = AssignDeliveryForm(request.POST)
            if assign_form.is_valid():
                delivery_man = assign_form.cleaned_data['delivery_man']
                order.assigned_to = delivery_man
                order.status = 'shipped' # Automatically set to 'shipped' when assigned
                order.save()
                messages.success(request, f"Order #{order.order_number} assigned to {delivery_man.user.username} and status set to Shipped.")
                return redirect('store:order_detail', order_id=order.id)
            
        elif is_assigned_delivery_man and 'update_status' in request.POST:
            new_status = request.POST.get('new_status')
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if new_status and new_status in valid_statuses:
                order.status = new_status
                order.save()
                messages.success(request, f"Order #{order.order_number} status updated to {new_status}.")
                return redirect('store:order_detail', order_id=order.id)
            else:
                messages.error(request, "Invalid status provided.")
        
        elif can_assign_delivery and 'update_payment_status' in request.POST:
            order.payment_status = 'paid'
            order.save()
            messages.success(request, f"Order #{order.order_number} payment status updated to paid.")
            return redirect('store:order_detail', order_id=order.id)
        
    # Initialize forms for GET requests or invalid POSTs
    if can_assign_delivery:
        assign_form = AssignDeliveryForm()

    if is_assigned_delivery_man:
        # Create a simple form for status update, pre-filling current status
        class OrderStatusUpdateForm(forms.Form):
            new_status = forms.ChoiceField(choices=Order.STATUS_CHOICES, initial=order.status, label="Update Status")
        status_form = OrderStatusUpdateForm()
    
    context = {
        'order': order,
        'can_assign_delivery': can_assign_delivery,
        'is_assigned_delivery_man': is_assigned_delivery_man,
        'assign_form': assign_form,
        'status_form': status_form,
        'STATUS_CHOICES': Order.STATUS_CHOICES,
    }
    return render(request, 'store/order_detail.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify the authentication backend when logging in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
        return JsonResponse({'success': True, 'message': f'{product.name} added to wishlist!', 'action': 'added'})
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
        return JsonResponse({'success': True, 'message': f'{product.name} is already in your wishlist!', 'action': 'exists'})


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    messages.success(request, 'Item removed from wishlist!')
    return JsonResponse({'success': True, 'message': 'Item removed from wishlist!', 'action': 'removed'})


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

def review_list(request):
    """List all product reviews"""
    reviews = Review.objects.all().order_by('-created_at')
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reviews': page_obj
    }
    return render(request, 'store/review_list.html', context)


@login_required
def user_profile(request):
    """User profile page with editable information"""
    user = request.user
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('store:user_profile')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('store:user_profile')
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = CustomPasswordChangeForm(user)
    
    context = {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'store/user_profile.html', context)