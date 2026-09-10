from django.contrib import admin
from .models import StockItem, StockUploadLog

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display=['qb_code','description','uom','category','current_stock']
    search_fields=['qb_code','description']

@admin.register(StockUploadLog)
class StockUploadLogAdmin(admin.ModelAdmin):
    list_display=['filename','uploaded_by','rows_created','rows_updated','uploaded_at']
    def has_add_permission(self,request): return False
