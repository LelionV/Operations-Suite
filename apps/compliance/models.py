
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class ComplianceRequirement(AuditMixin):
    class Category(models.TextChoices):
        LAW        = "LAW",      "Law / Legislation"
        REGULATION = "REG",      "Regulation"
        STANDARD   = "STD",      "Standard"
        POLICY     = "POL",      "Company Policy"
        PERMIT     = "PERMIT",   "Permit Condition"
        OTHER      = "OTHER",    "Other"
    class Status(models.TextChoices):
        COMPLIANT     = "COMPLIANT",     "Compliant"
        PARTIAL       = "PARTIAL",       "Partially Compliant"
        NON_COMPLIANT = "NON_COMPLIANT", "Non-Compliant"
        NOT_ASSESSED  = "NOT_ASSESSED",  "Not Assessed"
    title         = models.CharField(max_length=300)
    reference     = models.CharField(max_length=100, blank=True, help_text="e.g. OSHA 29 CFR 1910.132")
    category      = models.CharField(max_length=20, choices=Category.choices, default=Category.LAW)
    description   = models.TextField(blank=True)
    applicable_to = models.TextField(blank=True, help_text="Departments/sites this applies to")
    owner         = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="compliance_owned")
    status        = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_ASSESSED)
    review_date   = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)

    class Meta: ordering = ["category","title"]
    def __str__(self): return self.title

    @property
    def status_css(self):
        return {"COMPLIANT":"success","PARTIAL":"warning","NON_COMPLIANT":"danger","NOT_ASSESSED":"muted"}.get(self.status,"muted")
