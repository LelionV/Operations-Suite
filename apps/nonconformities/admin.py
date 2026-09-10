
from django.contrib import admin
from .models import NonConformity
@admin.register(NonConformity)
class NCA(admin.ModelAdmin):
    list_display=["title","category","severity","status","responsible_person","due_date"]
    list_filter=["category","severity","status"]; search_fields=["title"]
