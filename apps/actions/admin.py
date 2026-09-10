
from django.contrib import admin
from .models import Action
@admin.register(Action)
class AA(admin.ModelAdmin):
    list_display=["title","action_type","priority","status","owner","due_date"]
    list_filter=["action_type","priority","status"]; search_fields=["title"]
