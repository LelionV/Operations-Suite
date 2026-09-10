from django.contrib import admin

from .models import Incident
@admin.register(Incident)
class IA(admin.ModelAdmin):
    list_display=["title","incident_type","severity","status","incident_date","department"]
    list_filter=["incident_type","severity","status"]; search_fields=["title"]
    date_hierarchy="incident_date"
