from .cart import SessionCart

def cart(request):
    """
    Контекстный процессор для добавления корзины в контекст всех шаблонов
    """
    return {'cart': SessionCart(request)}
