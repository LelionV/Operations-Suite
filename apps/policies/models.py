
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class PolicyDocument(AuditMixin):
    class DocType(models.TextChoices):
        POLICY    = "POLICY",    "Policy"
        SOP       = "SOP",       "SOP / Procedure"
        GUIDELINE = "GUIDE",     "Guideline"
        FORM      = "FORM",      "Form / Template"
        OTHER     = "OTHER",     "Other"
    class Status(models.TextChoices):
        DRAFT    = "DRAFT",    "Draft"
        REVIEW   = "REVIEW",   "Under Review"
        APPROVED = "APPROVED", "Approved"
        OBSOLETE = "OBSOLETE", "Obsolete"

    title        = models.CharField(max_length=300)
    doc_number   = models.CharField(max_length=50, unique=True)
    doc_type     = models.CharField(max_length=10, choices=DocType.choices, default=DocType.POLICY)
    version      = models.CharField(max_length=20, default="1.0")
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    description  = models.TextField(blank=True)
    file         = models.FileField(upload_to="policies/", null=True, blank=True)
    approved_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                    on_delete=models.SET_NULL, related_name="policies_approved")
    approved_at  = models.DateTimeField(null=True, blank=True)
    review_date  = models.DateField(null=True, blank=True)
    expiry_date  = models.DateField(null=True, blank=True)
    departments = models.ManyToManyField(
        "departments.Department",
        blank=True,
    )    
    requires_acknowledgement = models.BooleanField(default=False)

    class Meta: ordering=["doc_type","title"]
    def __str__(self): return f"{self.doc_number} — {self.title}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date and self.expiry_date < timezone.now().date()

    @property
    def status_css(self):
        return {"APPROVED":"success","REVIEW":"warning","DRAFT":"muted","OBSOLETE":"danger"}.get(self.status,"muted")


class PolicyAcknowledgement(models.Model):
    policy     = models.ForeignKey(PolicyDocument, on_delete=models.CASCADE, related_name="acknowledgements")
    employee   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="policy_acks")
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    notes      = models.TextField(blank=True)
    class Meta: unique_together=[("policy","employee")]
    def __str__(self): return f"{self.employee} ack {self.policy.doc_number}"
