from django.contrib import admin
from .models import ImportedProduct

@admin.register(ImportedProduct)
class ImportedProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'cost_price', 'selling_price', 'quantity_imported', 'import_date', 'store_product')
    list_filter = ('supplier', 'import_date', 'category')
    search_fields = ('name', 'description', 'supplier')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('store_product', 'category') # For easier selection of related objects
    date_hierarchy = 'import_date'
    # Optionally, you can make these fields read-only in the admin if you want them to be managed by the save method only
    # readonly_fields = ('store_product',)
