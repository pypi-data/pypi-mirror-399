from django.conf import settings
from .models import Product, Cart


class SessionCart:
    """
    Класс для работы с корзиной через сессии
    """

    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # Сохраняем пустую корзину в сессии
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Добавить товар в корзину или обновить его количество
        Используем code вместо id
        """
        product_code = str(product.code)

        if product_code not in self.cart:
            self.cart[product_code] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,
                'product_id': product.code  # Используем code как идентификатор
            }

        if update_quantity:
            self.cart[product_code]['quantity'] = quantity
        else:
            self.cart[product_code]['quantity'] += quantity

        # Гарантируем, что количество не отрицательное
        if self.cart[product_code]['quantity'] < 1:
            self.remove(product)
            return

        self.save()

        # Синхронизируем с БД если пользователь авторизован
        if self.request.user.is_authenticated:
            self._sync_with_db()

    def save(self):
        """
        Сохранить корзину в сессии
        """
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        """
        Удалить товар из корзины по code
        """
        product_code = str(product.code)

        if product_code in self.cart:
            del self.cart[product_code]
            self.save()

            # Синхронизируем с БД если пользователь авторизован
            if self.request.user.is_authenticated:
                self._sync_with_db()

    def remove_by_code(self, product_code):
        """
        Удалить товар из корзины по code без объекта продукта
        """
        product_code = str(product_code)

        if product_code in self.cart:
            del self.cart[product_code]
            self.save()

            # Синхронизируем с БД если пользователь авторизован
            if self.request.user.is_authenticated:
                self._sync_with_db()

    def clear(self):
        """
        Очистить корзину
        """
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True

        # Синхронизируем с БД если пользователь авторизован
        if self.request.user.is_authenticated:
            self._sync_with_db(clear=True)

    def get_total_price(self):
        """
        Получить общую стоимость товаров в корзине
        """
        total = 0
        for item in self.cart.values():
            total += float(item['price']) * item['quantity']
        return total

    def get_cart_summary(self):
        """
        Получить краткую информацию о корзине
        """
        return {
            'total_items': len(self),
            'total_price': float(self.get_total_price()),
            'items': list(self.cart.values())
        }

    def __iter__(self):
        """
        Итерация по товарам в корзине
        """
        product_codes = self.cart.keys()
        products = Product.objects.filter(code__in=product_codes)

        # Создаем словарь продуктов для быстрого доступа
        products_dict = {product.code: product for product in products}

        # Создаем копию корзины для итерации
        cart_copy = {}

        # Проходим по всем товарам в корзине
        for product_code, item in self.cart.items():
            if product_code in products_dict:
                item_copy = item.copy()
                item_copy['product'] = products_dict[product_code]
                item_copy['price_decimal'] = float(item['price'])
                item_copy['total_price'] = item_copy['price_decimal'] * item['quantity']
                cart_copy[product_code] = item_copy

        # Удаляем из сессии товары, которых нет в базе
        codes_to_remove = []
        for product_code in self.cart.keys():
            if product_code not in products_dict:
                codes_to_remove.append(product_code)

        if codes_to_remove:
            for code in codes_to_remove:
                if code in self.cart:
                    del self.cart[code]
            self.save()

        # Генерируем элементы
        for item in cart_copy.values():
            yield item

    def __len__(self):
        """
        Получить общее количество товаров в корзине
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_product_quantity(self, product_code):
        """
        Получить количество конкретного товара в корзине
        """
        product_code = str(product_code)
        return self.cart.get(product_code, {}).get('quantity', 0)

    def _sync_with_db(self, clear=False):
        """
        Синхронизировать корзину из сессии с БД
        """
        if not self.request.user.is_authenticated:
            return

        try:
            # Получаем или создаем корзину пользователя
            cart_db, created = Cart.objects.get_or_create(
                user=self.request.user,
                defaults={'products': self.cart if not clear else {}}
            )

            if not created:
                if clear:
                    cart_db.products = {}
                else:
                    cart_db.products = self.cart
                cart_db.save()
        except Exception as e:
            print(f"Error syncing cart with DB: {e}")
