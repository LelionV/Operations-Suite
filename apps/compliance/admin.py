
from django.contrib import admin
from .models import ComplianceRequirement
@admin.register(ComplianceRequirement)
class CRA(admin.ModelAdmin):
    list_display=["title","category","status","owner","review_date"]
    list_filter=["category","status"]
    search_fields=["title","reference"]
