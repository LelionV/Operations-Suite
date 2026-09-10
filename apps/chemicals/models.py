
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class Chemical(AuditMixin):
    class HazardClass(models.TextChoices):
        FLAMMABLE="FLAMMABLE","Flammable"
        CORROSIVE="CORROSIVE","Corrosive"
        TOXIC="TOXIC","Toxic"
        EXPLOSIVE="EXPLOSIVE","Explosive"
        OXIDISER="OXIDISER","Oxidiser"
        IRRITANT="IRRITANT","Irritant"
        ENVIRONMENTAL="ENVIRONMENTAL","Environmental Hazard"
        NON_HAZARDOUS="NONE","Non-Hazardous"

    chemical_name = models.CharField(max_length=255)
    cas_number    = models.CharField(max_length=20, blank=True, help_text="CAS Registry Number")
    product_code  = models.CharField(max_length=50, blank=True)
    supplier      = models.ForeignKey("contractors.Contractor", null=True, blank=True, on_delete=models.SET_NULL, related_name="chemicals")
    hazard_class  = models.CharField(max_length=20, choices=HazardClass.choices, default=HazardClass.NON_HAZARDOUS)
    hazard_description = models.TextField(blank=True)
    storage_location = models.CharField(max_length=255, blank=True)
    department    = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    site          = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit          = models.CharField(max_length=20, blank=True, help_text="e.g. L, kg")
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expiry_date   = models.DateField(null=True, blank=True)
    sds_file      = models.FileField(upload_to="sds/", null=True, blank=True, verbose_name="SDS/MSDS File")
    sds_date      = models.DateField(null=True, blank=True, verbose_name="SDS Issue Date")
    required_ppe  = models.TextField(blank=True, help_text="PPE required when handling")
    handling_requirements = models.TextField(blank=True)
    storage_requirements  = models.TextField(blank=True)
    disposal_method = models.TextField(blank=True)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="chemicals_responsible")
    is_active     = models.BooleanField(default=True)
    notes         = models.TextField(blank=True)

    class Meta: ordering=["chemical_name"]
    def __str__(self): return self.chemical_name

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date and self.expiry_date < timezone.now().date()

    @property
    def hazard_css(self):
        return {"FLAMMABLE":"warning","CORROSIVE":"danger","TOXIC":"danger","EXPLOSIVE":"danger",
                "OXIDISER":"warning","IRRITANT":"hod","ENVIRONMENTAL":"head","NONE":"approved"}.get(self.hazard_class,"draft")
