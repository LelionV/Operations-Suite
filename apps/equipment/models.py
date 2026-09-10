
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin
from django.utils import timezone

class EquipmentCategory(models.Model):
    name=models.CharField(max_length=100, unique=True)
    inspection_interval_days=models.PositiveIntegerField(default=365, help_text="Default inspection interval in days")
    class Meta: ordering=["name"]
    def __str__(self): return self.name

class Equipment(AuditMixin):
    class Status(models.TextChoices):
        OPERATIONAL = "OPERATIONAL","Operational"
        UNDER_MAINT = "UNDER_MAINT","Under Maintenance"
        OUT_OF_SERVICE="OUT_OF_SERVICE","Out of Service"
        DECOMMISSIONED="DECOMMISSIONED","Decommissioned"
    class Condition(models.TextChoices):
        EXCELLENT="EXCELLENT","Excellent"
        GOOD="GOOD","Good"
        FAIR="FAIR","Fair"
        POOR="POOR","Poor"

    asset_id       = models.CharField(max_length=50, unique=True)
    name           = models.CharField(max_length=255)
    category       = models.ForeignKey(EquipmentCategory, on_delete=models.PROTECT, related_name="equipment")
    description    = models.TextField(blank=True)
    make           = models.CharField(max_length=100, blank=True)
    model_number   = models.CharField(max_length=100, blank=True)
    serial_number  = models.CharField(max_length=100, blank=True)
    location       = models.CharField(max_length=255, blank=True)
    department     = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL, related_name="equipment")
    site           = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL, related_name="equipment")
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="equipment_responsible")
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL)
    condition      = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    purchase_date  = models.DateField(null=True, blank=True)
    purchase_cost  = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    warranty_expiry= models.DateField(null=True, blank=True)
    last_inspection= models.DateField(null=True, blank=True)
    next_inspection= models.DateField(null=True, blank=True)
    last_maintenance=models.DateField(null=True, blank=True)
    next_maintenance=models.DateField(null=True, blank=True)
    calibration_due= models.DateField(null=True, blank=True)
    notes          = models.TextField(blank=True)
    is_safety_critical = models.BooleanField(default=False, help_text="Fire extinguisher, emergency equipment etc.")

    class Meta: ordering=["category","asset_id"]
    def __str__(self): return f"{self.asset_id} — {self.name}"

    @property
    def status_css(self):
        return {"OPERATIONAL":"success","UNDER_MAINT":"warning","OUT_OF_SERVICE":"danger","DECOMMISSIONED":"muted"}.get(self.status,"draft")

    @property
    def inspection_overdue(self):
        if not self.next_inspection: return False
        return self.next_inspection < timezone.now().date()

    @property
    def maintenance_overdue(self):
        if not self.next_maintenance: return False
        return self.next_maintenance < timezone.now().date()
