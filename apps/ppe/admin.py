
from django.contrib import admin
from .models import PPEItem, PPEType, PPERequirement
@admin.register(PPEType)
class PTA(admin.ModelAdmin): list_display=["name","lifespan_months","standard"]
@admin.register(PPEItem)
class PIA(admin.ModelAdmin):
    list_display=["item_code","ppe_type","status","condition","issued_to","expiry_date"]
    list_filter=["status","condition","ppe_type"]; search_fields=["item_code"]
@admin.register(PPERequirement)
class PRA(admin.ModelAdmin): list_display=["department","ppe_type","job_role","is_mandatory"]
