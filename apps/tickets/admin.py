from django.contrib import admin
from .models import Ticket, TicketComment, TicketAttachment, TicketOverdue


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['sender', 'created_at']


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at', 'filename']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ['code', 'title', 'department', 'priority', 'status',
                     'created_by', 'is_overdue', 'created_at']
    list_filter   = ['status', 'priority', 'department']
    search_fields = ['code', 'title', 'created_by__username']
    readonly_fields = ['code', 'created_at', 'updated_at', 'resolved_at', 'closed_at']
    inlines       = [TicketCommentInline, TicketAttachmentInline]

    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(TicketOverdue)
class TicketOverdueAdmin(admin.ModelAdmin):
    list_display  = ['ticket', 'notification_count', 'last_notified_at']
    readonly_fields = ['ticket', 'first_detected_at', 'last_notified_at',
                       'notification_count', 'created_at', 'updated_at']
