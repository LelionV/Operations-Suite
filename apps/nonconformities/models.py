
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class NonConformity(AuditMixin):
    class Category(models.TextChoices):
        FINDING    = "FINDING",    "Finding"
        VIOLATION  = "VIOLATION",  "Violation"
        OBSERVATION= "OBSERVATION","Observation"
        OFI        = "OFI",        "Opportunity for Improvement"
    class Severity(models.TextChoices):
        MAJOR  = "MAJOR",  "Major"
        MINOR  = "MINOR",  "Minor"
        OBS    = "OBS",    "Observation"
    class Status(models.TextChoices):
        OPEN     = "OPEN",     "Open"
        IN_PROGRESS="IN_PROGRESS","In Progress"
        CLOSED   = "CLOSED",   "Closed"
        VERIFIED = "VERIFIED", "Verified Closed"

    title         = models.CharField(max_length=300)
    category      = models.CharField(max_length=20, choices=Category.choices, default=Category.FINDING)
    severity      = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MINOR)
    status        = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    source        = models.CharField(max_length=100, blank=True, help_text="e.g. Internal Audit, Inspection, Incident")
    audit         = models.ForeignKey("audits.Audit", null=True, blank=True, on_delete=models.SET_NULL, related_name="nonconformities")
    inspection    = models.ForeignKey("inspections.Inspection", null=True, blank=True, on_delete=models.SET_NULL, related_name="nonconformities")
    department    = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    site          = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    description   = models.TextField()
    requirement   = models.TextField(blank=True, help_text="What requirement was not met")
    root_cause    = models.TextField(blank=True)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="nc_responsible")
    due_date      = models.DateField(null=True, blank=True)
    closed_date   = models.DateField(null=True, blank=True)
    verified_by   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="nc_verified")
    notes         = models.TextField(blank=True)

    class Meta: ordering=["-created_at"]
    def __str__(self): return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date and self.status not in ("CLOSED","VERIFIED") and self.due_date < timezone.now().date()

    @property
    def severity_css(self):
        return {"MAJOR":"danger","MINOR":"warning","OBS":"head"}.get(self.severity,"draft")

    @property
    def status_css(self):
        return {"OPEN":"danger","IN_PROGRESS":"warning","CLOSED":"approved","VERIFIED":"head"}.get(self.status,"draft")
