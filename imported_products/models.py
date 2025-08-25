from django.db import models
from store.models import Product, Category # Assuming Category is also needed for product creation

class ImportedProduct(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Adding selling_price to ImportedProduct as well for initial pricing
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.CharField(max_length=255, blank=True)
    import_date = models.DateField(auto_now_add=True)
    quantity_imported = models.IntegerField(default=1)
    # Link to the actual Product in the store app
    store_product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='imported_versions'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Imported Product'
        verbose_name_plural = 'Imported Products'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.utils.text import slugify

        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique, append a number if necessary
            original_slug = self.slug
            num = 1
            while ImportedProduct.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1

        super().save(*args, **kwargs)

        # Create or update the corresponding Product in the store app
        if self.store_product:
            # Update existing product
            product = self.store_product
            product.name = self.name
            product.slug = self.slug
            product.description = self.description
            product.price = self.selling_price if self.selling_price is not None else self.cost_price # Use selling price if available
            product.stock += self.quantity_imported # Add imported quantity to existing stock
            if self.category: # Update category if provided
                product.category = self.category
            product.save()
        else:
            # Create a new product
            # Ensure a category is present for the new product
            if self.category is None:
                # Fallback to a default category if none is provided
                # Or create a default one if it doesn't exist
                default_category, created = Category.objects.get_or_create(
                    name='Uncategorized', slug='uncategorized'
                )
                self.category = default_category

            product = Product.objects.create(
                name=self.name,
                slug=self.slug,
                description=self.description,
                price=self.selling_price if self.selling_price is not None else self.cost_price,
                category=self.category,
                stock=self.quantity_imported,
                available=True, # Imported products are available by default
            )
            self.store_product = product
            self.save() # Save ImportedProduct again to link to the new store_product
