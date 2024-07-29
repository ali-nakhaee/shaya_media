""" shop.urls """

from django.urls import path

from . import views

app_name = 'shop'
urlpatterns = [
    path('pricing/', views.Pricing.as_view(), name='pricing'),
    path('edit_price/<int:price_id>/', views.EditPrice.as_view(), name='edit_price'),
    path('cart/', views.Cart.as_view(), name='cart'),
    path('orders/', views.Orders.as_view(), name='orders'),
]