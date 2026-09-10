from django.contrib import admin
from .models import ProcurementOrder, ProcurementLineItem


class ProcurementLineItemInline(admin.TabularInline):
    model = ProcurementLineItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(ProcurementOrder)
class ProcurementOrderAdmin(admin.ModelAdmin):
    list_display  = ['purchase_order', 'supplier_name', 'status', 'ordered_at']
    list_filter   = ['status']
    search_fields = ['purchase_order__po_number', 'supplier_name', 'order_reference']
    readonly_fields = ['ordered_by', 'ordered_at', 'created_at', 'updated_at']
    inlines = [ProcurementLineItemInline]
