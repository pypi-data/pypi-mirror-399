# models/__init__.py
import json
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy
from .choices import AvailabilityChoices, OrderStatusChoices, MeasureChoices
from .default import default_article


class Product(models.Model):
    preview = models.ImageField(gettext_lazy('Preview'), upload_to='products/%Y/%m/%d')
    name = models.CharField(gettext_lazy('Name'), max_length=100)
    price = models.FloatField(gettext_lazy('Price'))
    code = models.CharField(gettext_lazy('Product code'), default=default_article, unique=True)
    availability = models.PositiveSmallIntegerField(gettext_lazy('Availability'), choices=AvailabilityChoices.choices,
                                                    default=AvailabilityChoices.AVAILABLE)
    measure = models.PositiveSmallIntegerField(gettext_lazy('Measure'), choices=MeasureChoices.choices,
                                               default=MeasureChoices.UNIT)

    class Meta:
        verbose_name = gettext_lazy('Product')
        verbose_name_plural = gettext_lazy('Products')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), models.CASCADE, verbose_name=gettext_lazy('User'),
                                related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name=gettext_lazy('Session key'))
    products = models.JSONField(verbose_name=gettext_lazy('Products'), default=dict)
    updated_at = models.DateTimeField(gettext_lazy('Updated at'), auto_now=True)

    class Meta:
        verbose_name = gettext_lazy('Cart')
        verbose_name_plural = gettext_lazy('Carts')

    def get_total_price(self):
        total = 0
        from django.db.models import Sum, F
        from . import Product

        product_ids = [int(pid) for pid in self.products.keys()]
        products_in_cart = Product.objects.filter(id__in=product_ids)

        for product in products_in_cart:
            quantity = self.products.get(str(product.id), 0)
            total += float(product.price) * float(quantity)

        return round(total, 2)


class Order(models.Model):
    client = models.ForeignKey(get_user_model(), models.PROTECT, 'orders', verbose_name=gettext_lazy('Client'))
    products = models.JSONField(verbose_name=gettext_lazy('Products'))
    order_date = models.DateTimeField(gettext_lazy('Order date'), auto_now_add=True)
    status = models.PositiveSmallIntegerField(gettext_lazy('Order status'), choices=OrderStatusChoices.choices,
                                              default=OrderStatusChoices.IS_BEING_PREPARED)
    status_date = models.DateTimeField(gettext_lazy('Order status change date'), auto_now=True)

    class Meta:
        verbose_name = gettext_lazy('Order')
        verbose_name_plural = gettext_lazy('Orders')
        ordering = ('order_date',)
