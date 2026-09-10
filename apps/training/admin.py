from django.contrib import admin

from .models import TrainingCourse, TrainingRecord
@admin.register(TrainingCourse)
class TCA(admin.ModelAdmin):
    list_display=["title","category","is_mandatory","validity_months"]
    search_fields=["title"]
@admin.register(TrainingRecord)
class TRA(admin.ModelAdmin):
    list_display=["employee","course","status","scheduled_date","expiry_date","score"]
    list_filter=["status","course"]
    search_fields=["employee__first_name","employee__last_name","course__title"]
