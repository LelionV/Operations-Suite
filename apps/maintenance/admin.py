
from django.contrib import admin
from .models import MaintenanceRecord
@admin.register(MaintenanceRecord)
class MRA(admin.ModelAdmin):
    list_display=["equipment","maintenance_type","title","status","scheduled_date","completed_date","certificate_expiry"]
    list_filter=["status","maintenance_type"]; search_fields=["title","equipment__asset_id","service_provider"]
