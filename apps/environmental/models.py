
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class EnvironmentalAspect(AuditMixin):
    class Category(models.TextChoices):
        WASTE="WASTE","Waste Management"
        WATER="WATER","Water Usage"
        ENERGY="ENERGY","Energy Consumption"
        EMISSIONS="EMISSIONS","Air Emissions"
        CHEMICAL="CHEMICAL","Chemical Handling"
        NOISE="NOISE","Noise"
        LAND="LAND","Land Contamination"
        OTHER="OTHER","Other"
    class Significance(models.TextChoices):
        HIGH="HIGH","High"; MEDIUM="MEDIUM","Medium"; LOW="LOW","Low"

    title         = models.CharField(max_length=300)
    category      = models.CharField(max_length=20, choices=Category.choices)
    description   = models.TextField(blank=True)
    activity      = models.CharField(max_length=255, blank=True)
    department    = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    site          = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    significance  = models.CharField(max_length=10, choices=Significance.choices, default=Significance.MEDIUM)
    legal_requirement = models.TextField(blank=True)
    current_controls  = models.TextField(blank=True)
    target_value  = models.CharField(max_length=100, blank=True)
    actual_value  = models.CharField(max_length=100, blank=True)
    unit_of_measure = models.CharField(max_length=50, blank=True)
    monitoring_frequency = models.CharField(max_length=100, blank=True)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="env_aspects")
    review_date   = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)

    class Meta: ordering=["category","title"]
    def __str__(self): return self.title
