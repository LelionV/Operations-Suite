
from django.contrib import admin
from .models import Equipment, EquipmentCategory
@admin.register(EquipmentCategory)
class ECA(admin.ModelAdmin): list_display=["name","inspection_interval_days"]
@admin.register(Equipment)
class EA(admin.ModelAdmin):
    list_display=["asset_id","name","category","status","condition","department","next_inspection","is_safety_critical"]
    list_filter=["status","condition","category","is_safety_critical","department"]
    search_fields=["asset_id","name","serial_number"]
