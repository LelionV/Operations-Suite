from django.contrib import admin

from .models import Contractor
@admin.register(Contractor)
class CA(admin.ModelAdmin):
    list_display=["name","status","contact_name","has_insurance","insurance_expiry","compliance_score","review_date"]
    list_filter=["status","has_insurance"]; search_fields=["name","contact_name"]
