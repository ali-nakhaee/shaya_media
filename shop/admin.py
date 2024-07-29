from django.contrib import admin

from .models import Price, Type, Subject, Level, Item, Order

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'level', 'price']
    list_display_links = ['id', 'subject', 'level', 'price']

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'unit']
    list_display_links = ['id', 'type', 'unit']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'subject']
    list_display_links = ['id', 'type', 'subject']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['id', 'level_num', 'title']
    list_display_links = ['id', 'level_num', 'title']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'level', 'subject', 'order', 'number', 'item_price']
    list_display_links = ['id', 'type', 'level', 'subject', 'order']

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'purchase_date', 'status', 'price']
    list_display_links = ['id', 'buyer', 'purchase_date']
    inlines = [ItemInline, ]

