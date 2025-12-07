from django.contrib import admin
from products.models import Product, Category, Size, ProductSize, ProductImage

# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(ProductSize)
admin.site.register(ProductImage)
