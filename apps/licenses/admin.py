from django.contrib import admin

from .models import License
@admin.register(License)
class LA(admin.ModelAdmin):
    list_display=["title","license_type","license_number","expiry_date","status","responsible_person"]
    list_filter=["license_type","status"]; search_fields=["title","license_number"]
