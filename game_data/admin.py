from django.contrib import admin

# Register your models here.
from django.utils.html import format_html

from .models import Hero, Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "icon")

    def icon(self, obj):
        return format_html(obj.image_html())


admin.site.register(Hero)
admin.site.register(Item, ItemAdmin)
