from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models import Avg # Import Avg


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True) # New field for Category image URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/category/{self.slug}/'

    def get_image_source(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return "/static/images/placeholder.html" # Default placeholder


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True) # New field for Product primary image URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/product/{self.slug}/'

    def get_image_source(self):
        # Prioritize direct image_url, then primary ProductImage, then direct image, then any other ProductImage
        if self.image_url:
            return self.image_url
        primary_product_image = self.images.filter(is_primary=True).first()
        if primary_product_image:
            return primary_product_image.get_image_source()
        if self.image:
            return self.image.url
        first_product_image = self.images.first()
        if first_product_image:
            return first_product_image.get_image_source()
        return "/static/images/placeholder.html" # Default placeholder

    def get_price(self):
        if self.sale_price:
            return self.sale_price
        return self.price

    def get_discount_percentage(self):
        if self.sale_price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount, 2)
        return 0

    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price

    def get_average_rating(self):
        # Use aggregate to calculate the average rating, returns None if no reviews
        return self.reviews.aggregate(Avg('rating'))['rating__avg']

    def is_in_flash_sale(self):
        from django.utils import timezone
        now = timezone.now()
        return self.flashsaleitem_set.filter(
            campaign__is_active=True,
            campaign__start_date__lte=now,
            campaign__end_date__gte=now,
            quantity_available__gt=0
        ).exists()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True) # New field for image URL
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.alt_text}"

    def get_image_source(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return "/static/images/placeholder.html" # Or a default placeholder image path


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart {self.id}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self):
        return self.product.get_price() * self.quantity


class DeliveryManManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__groups__name='DeliveryGroup') # Assuming a 'DeliveryGroup' exists

class DeliveryMan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager() # Default manager
    delivery_men = DeliveryManManager() # Custom manager

    class Meta:
        verbose_name_plural = 'Delivery Men'

    def __str__(self):
        return self.user.username


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'), # New status
        ('delivery_attempted', 'Delivery Attempted'), # New status
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(DeliveryMan, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries') # New field
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Payment information
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20, default='pending')
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import datetime
            import uuid
            # Generate a unique order number using timestamp and random string
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            self.order_number = f"ORD-{timestamp}-{unique_id}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self):
        return self.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Ad(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True)
    link = models.URLField(max_length=2000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Ads'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_image_source(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return "/static/images/placeholder.html"


class FlashSaleCampaign(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Flash Sale Campaigns'
        ordering = ['start_date']

    def __str__(self):
        return self.name

    def is_currently_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


class FlashSaleItem(models.Model):
    campaign = models.ForeignKey(FlashSaleCampaign, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['campaign', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} ({self.campaign.name})"

    def is_available(self):
        return self.campaign.is_currently_active() and self.quantity_available > 0

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Call the original save method first
        # Update the associated product's sale_price
        if self.product:
            # Fetch a fresh instance of the product to ensure we're not working with a stale object
            product_instance = self.product.__class__.objects.get(pk=self.product.pk)
            product_instance.sale_price = self.sale_price
            product_instance.save()