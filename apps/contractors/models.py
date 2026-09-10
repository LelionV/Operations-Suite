
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class Contractor(AuditMixin):
    class Status(models.TextChoices):
        APPROVED="APPROVED","Approved"; PENDING="PENDING","Pending Review"
        SUSPENDED="SUSPENDED","Suspended"; BLACKLISTED="BLACKLISTED","Blacklisted"

    name         = models.CharField(max_length=255)
    company_reg  = models.CharField(max_length=100, blank=True)
    contact_name = models.CharField(max_length=200, blank=True)
    contact_email= models.EmailField(blank=True)
    contact_phone= models.CharField(max_length=30, blank=True)
    services_provided = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="contractors_approved")
    approval_date= models.DateField(null=True, blank=True)
    review_date  = models.DateField(null=True, blank=True)
    # Required documents tracking
    has_insurance        = models.BooleanField(default=False)
    insurance_expiry     = models.DateField(null=True, blank=True)
    has_safety_policy    = models.BooleanField(default=False)
    has_method_statement = models.BooleanField(default=False)
    has_risk_assessment  = models.BooleanField(default=False)
    has_training_records = models.BooleanField(default=False)
    has_valid_license    = models.BooleanField(default=False)
    compliance_score     = models.PositiveIntegerField(default=0, help_text="0-100 compliance score")
    last_assessment_date = models.DateField(null=True, blank=True)
    notes        = models.TextField(blank=True)

    class Meta: ordering=["name"]
    def __str__(self): return self.name

    @property
    def status_css(self):
        return {"APPROVED":"approved","PENDING":"warning","SUSPENDED":"danger","BLACKLISTED":"danger"}.get(self.status,"draft")

    @property
    def insurance_expired(self):
        from django.utils import timezone
        return self.insurance_expiry and self.insurance_expiry < timezone.now().date()
