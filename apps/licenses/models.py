
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class License(AuditMixin):
    class LicenseType(models.TextChoices):
        BUSINESS="BUSINESS","Business License"
        EQUIPMENT="EQUIPMENT","Equipment Certificate"
        FIRE="FIRE","Fire Certificate"
        EMPLOYEE="EMPLOYEE","Employee Certificate/License"
        ENVIRONMENTAL="ENVIRONMENTAL","Environmental Permit"
        INSURANCE="INSURANCE","Insurance Policy"
        OPERATIONAL="OPERATIONAL","Operational Permit"
        OTHER="OTHER","Other"
    class Status(models.TextChoices):
        VALID="VALID","Valid"; EXPIRING="EXPIRING","Expiring Soon"; EXPIRED="EXPIRED","Expired"; PENDING="PENDING","Pending Renewal"

    title         = models.CharField(max_length=300)
    license_type  = models.CharField(max_length=20, choices=LicenseType.choices, default=LicenseType.OTHER)
    license_number= models.CharField(max_length=100, blank=True)
    issuing_authority = models.CharField(max_length=200, blank=True)
    holder        = models.CharField(max_length=200, blank=True, help_text="Person/entity holding this license")
    department    = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    site          = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    equipment     = models.ForeignKey("equipment.Equipment", null=True, blank=True, on_delete=models.SET_NULL, related_name="licenses")
    issue_date    = models.DateField(null=True, blank=True)
    expiry_date   = models.DateField(null=True, blank=True)
    renewal_lead_days = models.PositiveIntegerField(default=30, help_text="Alert this many days before expiry")
    document_file = models.FileField(upload_to="licenses/", null=True, blank=True)
    status        = models.CharField(max_length=20, choices=Status.choices, default=Status.VALID)
    reminder_sent = models.BooleanField(default=False)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="licenses_responsible")
    notes         = models.TextField(blank=True)

    class Meta: ordering=["expiry_date","title"]
    def __str__(self): return self.title

    @property
    def days_to_expiry(self):
        if not self.expiry_date: return None
        from django.utils import timezone
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expired(self):
        d=self.days_to_expiry; return d is not None and d<0

    @property
    def is_expiring_soon(self):
        d=self.days_to_expiry; return d is not None and 0<=d<=self.renewal_lead_days

    @property
    def status_css(self):
        if self.is_expired: return "danger"
        if self.is_expiring_soon: return "warning"
        return "approved"
