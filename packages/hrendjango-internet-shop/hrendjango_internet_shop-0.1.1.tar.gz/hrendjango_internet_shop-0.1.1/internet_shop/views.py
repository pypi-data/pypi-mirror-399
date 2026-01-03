from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from hrenpack.framework.django.views import View
from .models import Product, Cart
from .cart import SessionCart
from .utils import cart_data


class CartView(View):
    """
    Просмотр содержимого корзины
    """
    title = gettext_lazy('Cart')
    template_name = 'internet_shop/cart.html'

    def get(self, request):
        """
        Просмотр содержимого корзины
        Если запрос AJAX/JSON - возвращаем JSON, иначе HTML
        """
        cart = SessionCart(request)

        # Если это AJAX запрос или запрос JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            try:
                cart_items = []
                for item in cart:
                    cart_items.append({
                        'product': {
                            'id': item['product'].id,
                            'name': item['product'].name,
                            'price': str(item['product'].price),
                            'preview_url': item['product'].preview.url if item['product'].preview else None
                        },
                        'quantity': item['quantity'],
                        'total_price': float(item['total_price'])
                    })

                return JsonResponse({
                    'status': 'success',
                    'cart_items': cart_items,
                    'cart_total': len(cart),
                    'cart_total_price': float(cart.get_total_price()),
                    'cart_empty': len(cart) == 0
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

        # Обычный HTML запрос
        return render(request, self.template_name, self.get_context_data(cart=cart))


@require_POST
def cart_add(request, code):
    cart, product, quantity = cart_data(request, code)

    # Проверяем доступность товара
    if product.availability == 0:  # NOT_AVAILABLE
        return JsonResponse({
            'status': 'error',
            'message': 'This product is not available',
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        }, status=400)

    try:
        cart.add(product, quantity)

        # Получаем обновленную информацию о товаре в корзине
        product_in_cart = cart.cart.get(str(product.code))

        return JsonResponse({
            'status': 'success',
            'message': 'Product added to cart',
            'product': {
                'code': product.code,
                'name': product.name,
                'price': str(product.price),
                'quantity': product_in_cart['quantity'] if product_in_cart else quantity,
                'total': float(product.price) * (product_in_cart['quantity'] if product_in_cart else quantity)
            },
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        }, status=500)


@require_POST
def cart_remove(request, code):
    cart = SessionCart(request)

    # Ищем товар по code
    product = get_object_or_404(Product, code=code)

    try:
        cart.remove(product)

        return JsonResponse({
            'status': 'success',
            'message': 'Product removed from cart',
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        }, status=500)


@require_POST
def cart_update(request, code):
    cart, product, quantity = cart_data(request, code)

    if quantity > 0:
        cart.add(product, quantity, update_quantity=True)

        # Получаем обновленную информацию о товаре
        product_in_cart = cart.cart.get(str(product.code))

        return JsonResponse({
            'status': 'success',
            'message': 'Cart updated',
            'product': {
                'code': product.code,
                'name': product.name,
                'price': str(product.price),
                'quantity': product_in_cart['quantity'] if product_in_cart else quantity,
                'total': float(product.price) * (product_in_cart['quantity'] if product_in_cart else quantity)
            },
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    else:
        # Если количество 0 или меньше - удаляем товар
        cart.remove(product)
        return JsonResponse({
            'status': 'success',
            'message': 'Product removed from cart',
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })


@require_POST
def cart_clear(request):
    """
    Очистить корзину (JSON API)
    """
    cart = SessionCart(request)

    try:
        cart.clear()

        return JsonResponse({
            'status': 'success',
            'message': 'Cart cleared',
            'cart_total': 0,
            'cart_total_price': 0.0
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def cart_info(request):
    """
    Быстрая информация о корзине (для отображения в шапке)
    """
    cart = SessionCart(request)

    return JsonResponse({
        'status': 'success',
        'cart_total': len(cart),
        'cart_total_price': float(cart.get_total_price()),
        'cart_empty': len(cart) == 0
    })


@login_required
@require_POST
def cart_merge(request):
    """
    Слияние корзины из сессии с корзиной пользователя в БД
    """
    cart = SessionCart(request)

    try:
        # Получаем или создаем корзину пользователя
        user_cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'products': cart.cart}
        )

        if not created:
            # Сливаем корзины
            session_cart = cart.cart.copy()

            for product_code, item in session_cart.items():
                if product_code in user_cart.products:
                    user_cart.products[product_code]['quantity'] += item['quantity']
                else:
                    user_cart.products[product_code] = item

            user_cart.save()

        # Очищаем сессионную корзину
        cart.clear()

        return JsonResponse({
            'status': 'success',
            'message': 'Cart merged successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def cart_item_quantity(request, product_code):
    """
    Получить количество конкретного товара в корзине
    """
    cart = SessionCart(request)
    quantity = cart.get_product_quantity(product_code)

    return JsonResponse({
        'status': 'success',
        'product_code': product_code,
        'quantity': quantity
    })