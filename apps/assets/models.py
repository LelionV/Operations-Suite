from django.db import models
from django.conf import settings
from django.utils import timezone

class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    depreciation_years = models.PositiveIntegerField(default=5)
    class Meta: ordering=["name"]; verbose_name_plural="Asset Categories"
    def __str__(self): return self.name

class Asset(models.Model):
    class Status(models.TextChoices):
        ACTIVE="ACTIVE","Active"
        UNDER_REPAIR="UNDER_REPAIR","Under Repair"
        RETIRED="RETIRED","Retired"
        LOST="LOST","Lost / Stolen"
        DISPOSED="DISPOSED","Disposed"
    class Condition(models.TextChoices):
        EXCELLENT="EXCELLENT","Excellent"
        GOOD="GOOD","Good"
        FAIR="FAIR","Fair"
        POOR="POOR","Poor"

    asset_tag     = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    name          = models.CharField(max_length=255)
    category      = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name="assets")
    brand         = models.CharField(max_length=100, blank=True)
    model_number  = models.CharField(max_length=100, blank=True)
    description   = models.TextField(blank=True)
    status        = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    condition     = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    purchase_date  = models.DateField(null=True, blank=True)
    purchase_cost  = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    purchase_order = models.ForeignKey("purchase_orders.PurchaseOrder", null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="assets")
    warranty_expiry = models.DateField(null=True, blank=True)
    department    = models.ForeignKey("departments.Department", null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="assets")
    allocated_to  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="allocated_assets")
    allocated_at  = models.DateTimeField(null=True, blank=True)
    location      = models.CharField(max_length=255, blank=True)
    notes         = models.TextField(blank=True)
    created_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                        null=True, related_name="assets_created")
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    class Meta: ordering=["asset_tag"]
    def __str__(self): return f"{self.asset_tag} — {self.name}"

    @property
    def is_under_warranty(self):
        if not self.warranty_expiry: return None
        return timezone.now().date() <= self.warranty_expiry

    @property
    def depreciated_value(self):
        if not self.purchase_cost or not self.purchase_date: return None
        years = (timezone.now().date()-self.purchase_date).days/365.25
        life  = self.category.depreciation_years if self.category else 5
        if life<=0: return float(self.purchase_cost)
        return round(max(float(self.purchase_cost)-(float(self.purchase_cost)/life*years),0),2)

    @property
    def status_css(self):
        return {"ACTIVE":"approved","UNDER_REPAIR":"warning","RETIRED":"cancelled",
                "LOST":"rejected","DISPOSED":"cancelled"}.get(self.status,"draft")

class AssetMutation(models.Model):
    class MutationType(models.TextChoices):
        ALLOCATED="ALLOCATED","Allocated to User"
        DEALLOCATED="DEALLOCATED","Deallocated"
        TRANSFERRED="TRANSFERRED","Department Transfer"
        OFFBOARDED="OFFBOARDED","Offboarded"
        STATUS_CHANGE="STATUS","Status Change"
        NOTE="NOTE","Note Added"
    asset         = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="mutations")
    mutation_type = models.CharField(max_length=20, choices=MutationType.choices)
    actor         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                        related_name="asset_mutations")
    from_user     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="asset_mut_from")
    to_user       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="asset_mut_to")
    from_department = models.ForeignKey("departments.Department", null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="asset_mut_from")
    to_department   = models.ForeignKey("departments.Department", null=True, blank=True,
                        on_delete=models.SET_NULL, related_name="asset_mut_to")
    from_status   = models.CharField(max_length=20, blank=True)
    to_status     = models.CharField(max_length=20, blank=True)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return f"{self.asset.asset_tag} — {self.get_mutation_type_display()}"
