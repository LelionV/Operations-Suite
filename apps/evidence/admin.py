from django.contrib import admin

from .models import EvidenceFile
@admin.register(EvidenceFile)
class EFA(admin.ModelAdmin):
    list_display=["title","doc_type","module","related_to","uploaded_by","created_at"]
    list_filter=["doc_type","module"]; search_fields=["title","related_to","tags"]
