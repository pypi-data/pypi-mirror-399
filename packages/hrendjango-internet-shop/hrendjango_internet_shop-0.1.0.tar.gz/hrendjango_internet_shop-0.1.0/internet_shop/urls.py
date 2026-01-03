# internet_shop/urls.py
from django.urls import path
from . import views

app_name = 'internet_shop'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart_detail'),
    path('cart/add/<str:code>/', views.cart_add, name='cart_add'),
    path('cart/remove/<str:code>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<str:code>/', views.cart_update, name='cart_update'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
]