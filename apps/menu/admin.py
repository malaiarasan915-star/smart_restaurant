from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Dish


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order')
    list_editable = ('order',)
    search_fields = ('name',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_vegetarian', 'image_preview')
    list_filter = ('category', 'is_available', 'is_vegetarian')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_vegetarian')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px; height:60px; object-fit:cover; border-radius:6px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Image Preview'
