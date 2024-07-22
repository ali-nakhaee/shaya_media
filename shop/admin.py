from django.contrib import admin

from .models import Price

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'level', 'price']
    list_display_links = ['id', 'subject', 'level', 'price']

