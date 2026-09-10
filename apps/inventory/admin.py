from django.contrib import admin
from .models import QBItem, QBUploadLog


@admin.register(QBItem)
class QBItemAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'uom', 'is_active', 'uploaded_at']
    list_filter   = ['is_active', 'uom']
    search_fields = ['code', 'name']
    readonly_fields = ['uploaded_by', 'uploaded_at']


@admin.register(QBUploadLog)
class QBUploadLogAdmin(admin.ModelAdmin):
    list_display  = ['filename', 'uploaded_by', 'rows_total', 'rows_created',
                     'rows_updated', 'rows_skipped', 'uploaded_at']
    readonly_fields = ['uploaded_by', 'uploaded_at', 'filename', 'rows_total',
                       'rows_created', 'rows_updated', 'rows_skipped', 'notes']

    def has_add_permission(self, request):
        return False
