
from django.contrib import admin
from .models import RiskRegister
@admin.register(RiskRegister)
class RRA(admin.ModelAdmin):
    list_display=["title","risk_rating","status","owner","review_date"]
    list_filter=["status","department"]
    search_fields=["title"]
    def risk_rating(self,obj): return obj.risk_rating
    risk_rating.short_description="Risk Level"
