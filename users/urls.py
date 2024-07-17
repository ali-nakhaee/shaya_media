""" users.urls """

from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginPage.as_view(), name='login_page'),
]
