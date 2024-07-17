""" URL configuration for shaya_site project. """

from django.contrib import admin
from django.urls import path, include

from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include('blog.urls')),
    path("users/", include('users.urls')),
] + debug_toolbar_urls()
