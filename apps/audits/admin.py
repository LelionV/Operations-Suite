from django.contrib import admin

from .models import Audit
@admin.register(Audit)
class AA(admin.ModelAdmin):
    list_display=["title","audit_type","status","result","scheduled_date","department"]
    list_filter=["audit_type","status","result"]; search_fields=["title","auditor"]
