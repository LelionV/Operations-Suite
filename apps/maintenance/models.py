
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class MaintenanceRecord(AuditMixin):
    class MaintenanceType(models.TextChoices):
        PREVENTIVE  = "PREVENTIVE",  "Preventive Maintenance"
        CORRECTIVE  = "CORRECTIVE",  "Corrective / Repair"
        CALIBRATION = "CALIBRATION", "Calibration"
        INSPECTION_SERVICE = "SERVICE", "Inspection Service"
    class Status(models.TextChoices):
        SCHEDULED  = "SCHEDULED",  "Scheduled"
        IN_PROGRESS= "IN_PROGRESS","In Progress"
        COMPLETED  = "COMPLETED",  "Completed"
        OVERDUE    = "OVERDUE",    "Overdue"
        CANCELLED  = "CANCELLED",  "Cancelled"

    equipment        = models.ForeignKey("equipment.Equipment", on_delete=models.CASCADE, related_name="maintenance_records")
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    title            = models.CharField(max_length=255)
    description      = models.TextField(blank=True)
    service_provider = models.CharField(max_length=255, blank=True)
    technician       = models.CharField(max_length=255, blank=True)
    scheduled_date   = models.DateField()
    completed_date   = models.DateField(null=True, blank=True)
    next_due_date    = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    cost             = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    certificate_number = models.CharField(max_length=100, blank=True)
    certificate_expiry = models.DateField(null=True, blank=True)
    work_done        = models.TextField(blank=True)
    parts_used       = models.TextField(blank=True)
    notes            = models.TextField(blank=True)
    assigned_to      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="maintenance_assigned")

    class Meta: ordering=["-scheduled_date"]
    def __str__(self): return f"{self.equipment.asset_id} — {self.title}"

    @property
    def status_css(self):
        return {"SCHEDULED":"head","IN_PROGRESS":"hod","COMPLETED":"approved","OVERDUE":"danger","CANCELLED":"muted"}.get(self.status,"draft")

    @property
    def certificate_expired(self):
        from django.utils import timezone
        return self.certificate_expiry and self.certificate_expiry < timezone.now().date()
