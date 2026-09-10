from django.contrib import admin
from .models import GoodsReceivedNote, GRNLineItem


class GRNLineItemInline(admin.TabularInline):
    model = GRNLineItem
    extra = 0
    readonly_fields = ['qty_ordered', 'qty_outstanding', 'is_fully_received']


@admin.register(GoodsReceivedNote)
class GRNAdmin(admin.ModelAdmin):
    list_display  = ['grn_number', 'purchase_order', 'received_by', 'status', 'received_at']
    list_filter   = ['status']
    search_fields = ['grn_number', 'purchase_order__po_number']
    readonly_fields = ['grn_number', 'received_by', 'received_at', 'updated_at']
    inlines = [GRNLineItemInline]
