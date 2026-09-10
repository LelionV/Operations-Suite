
from django.contrib import admin
from .models import VisitorAppointment, VisitorLog, WhatsAppConfig

class LogInline(admin.TabularInline):
    model = VisitorLog; extra = 0; can_delete = False
    readonly_fields = ["actor","from_status","to_status","notes","created_at"]
    def has_add_permission(self, r, o=None): return False

@admin.register(VisitorAppointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ["ref_number","visitor_name","visitor_company","host_display",
                     "scheduled_date","scheduled_start","status","arrived_at"]
    list_filter   = ["status","scheduled_date","host_department"]
    search_fields = ["ref_number","visitor_name","visitor_company","visitor_phone","visitor_id_number"]
    readonly_fields = ["ref_number","arrived_at","checked_out_at","created_at","updated_at",
                       "host_notified_at","arrival_whatsapp_sent"]
    inlines = [LogInline]
    def host_display(self, obj): return obj.host_display
    host_display.short_description = "Host"

@admin.register(WhatsAppConfig)
class WAConfigAdmin(admin.ModelAdmin):
    list_display = ["name","provider","from_number","is_active","updated_at"]

@admin.register(VisitorLog)
class LogAdmin(admin.ModelAdmin):
    list_display = ["appointment","actor","from_status","to_status","created_at"]
    def has_add_permission(self, r): return False
    def has_change_permission(self, r, o=None): return False
