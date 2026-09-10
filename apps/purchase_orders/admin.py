from django.contrib import admin
from .models import PurchaseOrder, POLineItem, ApprovalLog


class POLineItemInline(admin.TabularInline):
    model = POLineItem
    extra = 0
    readonly_fields = ['total_price', 'is_rejected', 'rejection_reason', 'rejected_by', 'rejected_at']


class ApprovalLogInline(admin.TabularInline):
    model = ApprovalLog
    extra = 0
    readonly_fields = ['actor', 'from_status', 'to_status', 'comment', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display  = ['po_number', 'title', 'department', 'requester',
                     'total_amount', 'status', 'created_at']
    list_filter   = ['status', 'department']
    search_fields = ['po_number', 'title', 'requester__username']
    readonly_fields = ['po_number', 'total_amount', 'hod_approved_at',
                       'head_approved_at', 'sent_to_procurement_at', 'created_at', 'updated_at']
    inlines = [POLineItemInline, ApprovalLogInline]


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display  = ['purchase_order', 'actor', 'from_status', 'to_status', 'created_at']
    readonly_fields = ['purchase_order', 'actor', 'from_status', 'to_status',
                       'comment', 'affected_items', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
