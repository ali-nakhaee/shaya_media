""" shop.urls """

from django.urls import path

from . import views

app_name = 'shop'
urlpatterns = [
    path('pricing/', views.Pricing.as_view(), name='pricing'),
    path('edit-price/<int:price_id>/', views.EditPrice.as_view(), name='edit_price'),
    path('cart/', views.CartByCustomer.as_view(), name='cart'),
    path('orders/', views.Orders.as_view(), name='orders'),
    path('all-orders/', views.AllOrders.as_view(), name='all_orders'),
    path('cart-by-admin/', views.CartByAdmin.as_view(), name='cart_by_admin'),
]