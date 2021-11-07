from django.contrib import admin

# Register your models here.
from hon_api.models import ApiKey


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ["cookie"]
    readonly_fields = ["cookie"]


admin.site.register(ApiKey, ApiKeyAdmin)
