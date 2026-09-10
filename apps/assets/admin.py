from django.contrib import admin
from .models import Asset,AssetCategory,AssetMutation

@admin.register(AssetCategory)
class ACAdmin(admin.ModelAdmin):
    list_display=["name","depreciation_years"]; search_fields=["name"]

class AMInline(admin.TabularInline):
    model=AssetMutation; extra=0; can_delete=False
    readonly_fields=["mutation_type","actor","from_user","to_user","from_department","to_department","from_status","to_status","notes","created_at"]
    def has_add_permission(self,r,o=None): return False

@admin.register(Asset)
class AAdmin(admin.ModelAdmin):
    list_display=["asset_tag","name","category","department","allocated_to","status","condition","purchase_date"]
    list_filter=["status","condition","category","department"]
    search_fields=["asset_tag","name","serial_number","brand"]
    readonly_fields=["created_by","created_at","updated_at"]
    inlines=[AMInline]

@admin.register(AssetMutation)
class AMAdmin(admin.ModelAdmin):
    list_display=["asset","mutation_type","actor","from_user","to_user","created_at"]
    list_filter=["mutation_type"]
    def has_add_permission(self,r): return False
    def has_change_permission(self,r,o=None): return False
