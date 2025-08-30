from django.contrib import admin
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Order, OrderItem, Wishlist, Ad, FlashSaleCampaign, FlashSaleItem
from django.utils.html import mark_safe
from django.db import transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image_url', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'description', 'image', 'image_url')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_url', 'alt_text', 'is_primary')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'sale_price', 'stock', 'available', 'featured', 'image_url', 'created_at']
    list_filter = ['available', 'featured', 'category', 'created_at']
    list_editable = ['price', 'sale_price', 'stock', 'available', 'featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fields = (
        'category', 'name', 'slug', 'description', 'price', 'sale_price',
        'stock', 'available', 'featured', 'image', 'image_url'
    )

    def save_model(self, request, obj, form, change):
        """
        When a product's sale_price is updated, update all FlashSaleItem(s) for this product
        to use the latest sale_price, unless their sale_price was manually set to something else.
        """
        old_obj = None
        if obj.pk:
            try:
                old_obj = Product.objects.get(pk=obj.pk)
            except Product.DoesNotExist:
                old_obj = None

        super().save_model(request, obj, form, change)

        # If the sale_price has changed, update all related FlashSaleItem(s)
        if old_obj and old_obj.sale_price != obj.sale_price:
            # Update all FlashSaleItem(s) for this product to use the new sale_price
            FlashSaleItem.objects.filter(product=obj).update(sale_price=obj.sale_price)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at', 'get_total_price']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_total_price']
    list_filter = ['created_at']
    search_fields = ['cart__user__username', 'product__name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    list_editable = ['status', 'payment_status']
    search_fields = ['order_number', 'user__username', 'email']
    readonly_fields = ['order_number', 'total_amount']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Shipping Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'stripe_payment_intent')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product__name']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'link', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']
    fields = ('name', 'image', 'image_url', 'link', 'is_active')


class FlashSaleItemInline(admin.TabularInline):
    model = FlashSaleItem
    extra = 0
    fields = ('product', 'sale_price', 'quantity_available', 'product_mini_image')
    readonly_fields = ('product_mini_image',)
    list_display = ('product', 'sale_price', 'quantity_available', 'product_mini_image')

    def product_mini_image(self, obj):
        if obj.product and obj.product.get_image_source():
            return mark_safe(f'<img src="{obj.product.get_image_source()}" width="50" height="50" style="object-fit: contain;" />')
        return "No Image"


@admin.register(FlashSaleCampaign)
class FlashSaleCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'is_currently_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name']
    list_editable = ['is_active']
    inlines = [FlashSaleItemInline]
    fields = ('name', 'start_date', 'end_date', 'is_active')
