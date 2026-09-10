from django.contrib import admin

from .models import EnvironmentalAspect
@admin.register(EnvironmentalAspect)
class EAA(admin.ModelAdmin):
    list_display=["title","category","significance","department","review_date"]
    list_filter=["category","significance"]; search_fields=["title"]
