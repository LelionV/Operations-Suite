from django.contrib import admin

from .models import EmergencyContact, EmergencyProcedure
@admin.register(EmergencyContact)
class ECA(admin.ModelAdmin):
    list_display=["name","role","phone_primary","department","is_active"]; list_filter=["is_active","department"]
@admin.register(EmergencyProcedure)
class EPA(admin.ModelAdmin):
    list_display=["title","emergency_type","site","last_drill_date","next_drill_date"]; list_filter=["emergency_type","site"]
