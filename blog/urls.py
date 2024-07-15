""" blog.urls file """

from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path('', views.PostList.as_view(), name='post_list'),
    path('add_post/', views.AddPost.as_view(), name='add_post'),
]