from django.contrib import admin
from .models import Product


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    ordering = ['name']
    list_per_page = 50
    search_fields = ['name']