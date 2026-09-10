from django.contrib import admin

from .models import Chemical
@admin.register(Chemical)
class CHA(admin.ModelAdmin):
    list_display=["chemical_name","cas_number","hazard_class","quantity_on_hand","unit","storage_location","expiry_date"]
    list_filter=["hazard_class","department"]; search_fields=["chemical_name","cas_number","product_code"]
