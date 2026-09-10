
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Site

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ["name","code","is_active"]
    search_fields = ["name","code"]

@admin.register(User)
class MergedUserAdmin(UserAdmin):
    list_display = ["username","get_full_name","email","department","site",
                    "osh_role","is_hod","is_head_approver","is_procurement_officer",
                    "is_storekeeper","is_gatekeeper","is_active"]
    list_filter  = ["osh_role","is_hod","is_head_approver","is_procurement_officer",
                    "is_storekeeper","is_stock_manager","is_asset_manager",
                    "is_gatekeeper","is_ticket_viewer","department","site","is_active"]
    search_fields = ["username","first_name","last_name","email","employee_id"]
    fieldsets = (
        (None, {"fields": ("username","password")}),
        ("Personal", {"fields": ("first_name","last_name","email","phone","job_title","employee_id")}),
        ("Organisation", {"fields": ("department","site")}),
        ("ProcureDesk Roles", {"fields": (
            "is_hod","is_head_approver","is_procurement_officer","is_storekeeper",
            "is_stock_manager","is_asset_manager","is_gatekeeper",
            "can_access_tickets","is_ticket_viewer"
        )}),
        ("OSH / EHS Role", {"fields": ("osh_role",)}),
        ("Permissions", {"fields": ("is_active","is_staff","is_superuser","groups","user_permissions"),
                          "classes": ("collapse",)}),
        ("Dates", {"fields": ("last_login","date_joined"), "classes": ("collapse",)}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "username","password1","password2","first_name","last_name","email",
            "department","site","osh_role",
            "is_hod","is_head_approver","is_procurement_officer","is_storekeeper",
            "is_stock_manager","is_asset_manager","is_gatekeeper","can_access_tickets","is_ticket_viewer"
        )}),
    )
    def get_full_name(self, obj): return obj.get_full_name() or "—"
    get_full_name.short_description = "Full Name"
