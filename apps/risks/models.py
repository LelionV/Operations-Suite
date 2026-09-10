
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class RiskRegister(AuditMixin):
    class Likelihood(models.IntegerChoices):
        RARE       = 1, "1 — Rare"
        UNLIKELY   = 2, "2 — Unlikely"
        POSSIBLE   = 3, "3 — Possible"
        LIKELY     = 4, "4 — Likely"
        ALMOST     = 5, "5 — Almost Certain"
    class Impact(models.IntegerChoices):
        NEGLIGIBLE = 1, "1 — Negligible"
        MINOR      = 2, "2 — Minor"
        MODERATE   = 3, "3 — Moderate"
        MAJOR      = 4, "4 — Major"
        CATASTROPHIC=5, "5 — Catastrophic"
    class Status(models.TextChoices):
        OPEN     = "OPEN",     "Open"
        MITIGATED= "MITIGATED","Mitigated"
        ACCEPTED = "ACCEPTED", "Accepted"
        CLOSED   = "CLOSED",   "Closed"

    title          = models.CharField(max_length=300)
    description    = models.TextField(blank=True)
    hazard_source  = models.CharField(max_length=200, blank=True)
    department     = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    site           = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL)
    likelihood     = models.IntegerField(choices=Likelihood.choices, default=3)
    impact         = models.IntegerField(choices=Impact.choices, default=3)
    likelihood_residual = models.IntegerField(choices=Likelihood.choices, null=True, blank=True)
    impact_residual     = models.IntegerField(choices=Impact.choices, null=True, blank=True)
    controls       = models.TextField(blank=True, help_text="Existing controls")
    mitigation_plan= models.TextField(blank=True)
    owner          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="risks_owned")
    review_date    = models.DateField(null=True, blank=True)
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    notes          = models.TextField(blank=True)

    class Meta: ordering = ["-created_at"]
    def __str__(self): return self.title

    @property
    def risk_score(self): return self.likelihood * self.impact
    @property
    def residual_risk_score(self):
        if self.likelihood_residual and self.impact_residual:
            return self.likelihood_residual * self.impact_residual
        return None
    @property
    def risk_level(self):
        s = self.risk_score
        if s >= 20: return ("CRITICAL", "danger")
        if s >= 12: return ("HIGH", "warning")
        if s >= 6:  return ("MEDIUM", "hod")
        return ("LOW", "approved")
    @property
    def risk_rating(self): return self.risk_level[0]
    @property
    def risk_css(self): return self.risk_level[1]
