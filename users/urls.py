""" users.urls """

from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
    path('check_password/', views.CheckPassword.as_view(), name='check_password'),
    path('user-settings/', views.UserSetting.as_view(), name='user_settings'),
]
