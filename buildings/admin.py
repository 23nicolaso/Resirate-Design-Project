from django.contrib import admin

from .models import Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["address", "borough", "zip_code"]
    search_fields = ["address", "borough", "zip_code"]
