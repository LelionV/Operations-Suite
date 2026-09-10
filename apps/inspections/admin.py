
from django.contrib import admin
from .models import Inspection, InspectionChecklist, ChecklistItem, InspectionResult
class ItemInline(admin.TabularInline):
    model=ChecklistItem; extra=1
@admin.register(InspectionChecklist)
class ICAdmin(admin.ModelAdmin):
    list_display=["name","category"]; inlines=[ItemInline]
@admin.register(Inspection)
class IA(admin.ModelAdmin):
    list_display=["title","inspection_type","status","inspector","scheduled_date","overall_result"]
    list_filter=["status","inspection_type","department"]; search_fields=["title"]
