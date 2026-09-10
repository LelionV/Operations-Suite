
from django.contrib import admin
from .models import PolicyDocument, PolicyAcknowledgement
@admin.register(PolicyDocument)
class PDA(admin.ModelAdmin):
    list_display=["doc_number","title","doc_type","version","status","review_date","expiry_date"]
    list_filter=["doc_type","status"]
    search_fields=["title","doc_number"]
@admin.register(PolicyAcknowledgement)
class AckAdmin(admin.ModelAdmin):
    list_display=["policy","employee","acknowledged_at"]
