from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home and product pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('flash-sales/', views.flash_sale_list, name='flash_sale_list'), # New flash sale list URL
    
    # Cart functionality
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', views.buy_now_direct, name='buy_now_direct'), # New direct buy URL
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout and payment
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout_with_order'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # User account
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='user_profile'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Search
    path('search/', views.search_products, name='search_products'),
    # Reviews
    path('reviews/', views.review_list, name='review_list'),

    # Delivery Man features
    path('delivery/dashboard/', views.delivery_man_dashboard, name='delivery_man_dashboard'),
    path('delivery/update_status/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),
]
