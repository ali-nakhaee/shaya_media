""" users.urls """

from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
]
