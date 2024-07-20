""" shop.urls """

from django.urls import path

from . import views

app_name = 'shop'
urlpatterns = [
    path('pricing/', views.Pricing.as_view(), name='pricing'),
]