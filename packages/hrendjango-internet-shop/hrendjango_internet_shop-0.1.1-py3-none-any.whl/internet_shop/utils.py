import json
from dataclasses import dataclass
from django.shortcuts import get_object_or_404
from .cart import SessionCart
from .models import Product


@dataclass
class CartData:
    cart: SessionCart
    product: Product
    quantity: int

    def __iter__(self):
        return iter([self.cart, self.product, self.quantity])


def cart_data(request, product_code) -> CartData:
    cart = SessionCart(request)

    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, KeyError, ValueError):
        quantity = int(request.POST.get('quantity', 1))

    return CartData(cart, get_object_or_404(Product, code=product_code), quantity)
