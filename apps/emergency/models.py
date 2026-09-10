
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class EmergencyContact(models.Model):
    name=models.CharField(max_length=200); role=models.CharField(max_length=100, blank=True)
    phone_primary=models.CharField(max_length=30); phone_secondary=models.CharField(max_length=30, blank=True)
    email=models.EmailField(blank=True)
    department=models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    site=models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    is_active=models.BooleanField(default=True); order=models.PositiveIntegerField(default=0)
    class Meta: ordering=["order","name"]
    def __str__(self): return f"{self.name} ({self.role})"

class EmergencyProcedure(AuditMixin):
    class EmergencyType(models.TextChoices):
        FIRE="FIRE","Fire"; MEDICAL="MEDICAL","Medical Emergency"
        CHEMICAL_SPILL="SPILL","Chemical Spill"; EVACUATION="EVACUATION","Evacuation"
        EARTHQUAKE="EARTHQUAKE","Earthquake"; FLOOD="FLOOD","Flood"; POWER="POWER","Power Failure"; OTHER="OTHER","Other"
    title=models.CharField(max_length=255)
    emergency_type=models.CharField(max_length=20, choices=EmergencyType.choices, default=EmergencyType.FIRE)
    site=models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    procedure_document=models.FileField(upload_to="emergency_procedures/", null=True, blank=True)
    procedure_text=models.TextField(blank=True, help_text="Step-by-step procedure")
    assembly_points=models.TextField(blank=True)
    evacuation_routes=models.TextField(blank=True)
    last_reviewed=models.DateField(null=True, blank=True)
    next_review=models.DateField(null=True, blank=True)
    last_drill_date=models.DateField(null=True, blank=True)
    next_drill_date=models.DateField(null=True, blank=True)
    notes=models.TextField(blank=True)
    class Meta: ordering=["emergency_type","title"]
    def __str__(self): return self.title
