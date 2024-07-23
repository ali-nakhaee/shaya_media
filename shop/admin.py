from django.contrib import admin

from .models import Price, Type, Subject, Level

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
