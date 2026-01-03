from django.conf import settings
from django.contrib import admin
from .models import Product, Cart

admin.site.register(Product)
# admin.site.register(Order)
admin.site.register(Cart)