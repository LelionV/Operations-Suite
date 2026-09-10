
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class PPEType(models.Model):
    name=models.CharField(max_length=100, unique=True)
    description=models.TextField(blank=True)
    hazard_protected=models.CharField(max_length=200, blank=True)
    standard=models.CharField(max_length=100, blank=True, help_text="e.g. EN 166, ANSI Z87")
    lifespan_months=models.PositiveIntegerField(default=12, help_text="Expected lifespan in months")
    class Meta: ordering=["name"]
    def __str__(self): return self.name

class PPEItem(AuditMixin):
    class Status(models.TextChoices):
        AVAILABLE="AVAILABLE","Available"
        ISSUED="ISSUED","Issued"
        DAMAGED="DAMAGED","Damaged"
        EXPIRED="EXPIRED","Expired"
        DECOMMISSIONED="DECOMMISSIONED","Decommissioned"
    class Condition(models.TextChoices):
        GOOD="GOOD","Good"; FAIR="FAIR","Fair"; POOR="POOR","Poor"

    ppe_type      = models.ForeignKey(PPEType, on_delete=models.PROTECT, related_name="items")
    item_code     = models.CharField(max_length=50, unique=True)
    brand         = models.CharField(max_length=100, blank=True)
    size          = models.CharField(max_length=30, blank=True)
    status        = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    condition     = models.CharField(max_length=10, choices=Condition.choices, default=Condition.GOOD)
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date   = models.DateField(null=True, blank=True)
    issued_to     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="ppe_issued")
    issued_date   = models.DateField(null=True, blank=True)
    return_date   = models.DateField(null=True, blank=True)
    department    = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    notes         = models.TextField(blank=True)

    class Meta: ordering=["ppe_type","item_code"]
    def __str__(self): return f"{self.item_code} — {self.ppe_type.name}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date and self.expiry_date < timezone.now().date()

    @property
    def status_css(self):
        return {"AVAILABLE":"approved","ISSUED":"head","DAMAGED":"danger","EXPIRED":"danger","DECOMMISSIONED":"muted"}.get(self.status,"draft")

class PPERequirement(models.Model):
    department   = models.ForeignKey("departments.Department", on_delete=models.CASCADE, related_name="ppe_requirements")
    job_role     = models.CharField(max_length=200, blank=True)
    ppe_type     = models.ForeignKey(PPEType, on_delete=models.CASCADE)
    is_mandatory = models.BooleanField(default=True)
    notes        = models.TextField(blank=True)
    class Meta: ordering=["department","ppe_type"]
    def __str__(self): return f"{self.department} — {self.ppe_type}"
