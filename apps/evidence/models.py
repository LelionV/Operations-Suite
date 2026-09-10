
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin
import os

class EvidenceFile(AuditMixin):
    class DocType(models.TextChoices):
        PHOTO="PHOTO","Photo"; PDF="PDF","PDF Document"; CERTIFICATE="CERT","Certificate"
        REPORT="REPORT","Report"; SIGNATURE="SIG","Signature"; TRAINING="TRAINING","Training Record"; OTHER="OTHER","Other"

    title=models.CharField(max_length=255)
    doc_type=models.CharField(max_length=20, choices=DocType.choices, default=DocType.OTHER)
    file=models.FileField(upload_to="evidence/%Y/%m/")
    description=models.TextField(blank=True)
    # Generic linking fields
    related_to=models.CharField(max_length=100, blank=True, help_text="e.g. Inspection #123, Action #45")
    module=models.CharField(max_length=50, blank=True, help_text="Source module: inspections, incidents, etc.")
    object_id=models.PositiveIntegerField(null=True, blank=True)
    uploaded_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="evidence_uploaded")
    tags=models.CharField(max_length=300, blank=True, help_text="Comma-separated tags")

    class Meta: ordering=["-created_at"]
    def __str__(self): return self.title

    def filename(self): return os.path.basename(self.file.name) if self.file else ""
    def extension(self): return self.filename().split(".")[-1].upper() if "." in self.filename() else ""
