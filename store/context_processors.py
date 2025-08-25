from .models import Category, Cart

def categories_processor(request):
    """Make categories available in all templates"""
    try:
        categories = Category.objects.all()
    except Exception:
        categories = []
    
    return {
        'categories': categories,
    }

def cart_processor(request):
    """Make cart available in all templates"""
    cart = None
    try:
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # For anonymous users, we'll use session-based cart
            session_key = request.session.session_key
            if session_key:
                cart, created = Cart.objects.get_or_create(session_key=session_key)
    except Exception:
        # If there's any error, just return None for cart
        cart = None
    
    return {
        'cart': cart,
    }
