
from django.db import models
from django.conf import settings
from apps.shared import AuditMixin

class Action(AuditMixin):
    class ActionType(models.TextChoices):
        CORRECTIVE  = "CORRECTIVE",  "Corrective Action"
        PREVENTIVE  = "PREVENTIVE",  "Preventive Action"
        IMPROVEMENT = "IMPROVEMENT", "Improvement Action"
    class Priority(models.TextChoices):
        CRITICAL="CRITICAL","Critical"; HIGH="HIGH","High"; MEDIUM="MEDIUM","Medium"; LOW="LOW","Low"
    class Status(models.TextChoices):
        OPEN="OPEN","Open"; IN_PROGRESS="IN_PROGRESS","In Progress"
        COMPLETED="COMPLETED","Completed"; VERIFIED="VERIFIED","Verified"; OVERDUE="OVERDUE","Overdue"

    title        = models.CharField(max_length=300)
    action_type  = models.CharField(max_length=20, choices=ActionType.choices, default=ActionType.CORRECTIVE)
    priority     = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    source       = models.CharField(max_length=100, blank=True, help_text="What triggered this action")
    nonconformity= models.ForeignKey("nonconformities.NonConformity", null=True, blank=True, on_delete=models.SET_NULL, related_name="actions")
    incident     = models.ForeignKey("incidents.Incident", null=True, blank=True, on_delete=models.SET_NULL, related_name="actions")
    audit        = models.ForeignKey("audits.Audit", null=True, blank=True, on_delete=models.SET_NULL, related_name="actions")
    description  = models.TextField()
    root_cause   = models.TextField(blank=True)
    action_plan  = models.TextField(blank=True)
    owner        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="actions_owned")
    department   = models.ForeignKey("departments.Department", null=True, blank=True, on_delete=models.SET_NULL)
    due_date     = models.DateField(null=True, blank=True)
    completed_date=models.DateField(null=True, blank=True)
    evidence     = models.TextField(blank=True, help_text="Description of evidence provided")
    evidence_file= models.FileField(upload_to="action_evidence/", null=True, blank=True)
    verified_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="actions_verified")
    verified_date= models.DateField(null=True, blank=True)
    approved_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="actions_approved")
    notes        = models.TextField(blank=True)

    class Meta: ordering=["-created_at"]
    def __str__(self): return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date and self.status not in ("COMPLETED","VERIFIED") and self.due_date < timezone.now().date()

    @property
    def priority_css(self):
        return {"CRITICAL":"danger","HIGH":"warning","MEDIUM":"hod","LOW":"approved"}.get(self.priority,"draft")

    @property
    def status_css(self):
        return {"OPEN":"danger","IN_PROGRESS":"warning","COMPLETED":"head","VERIFIED":"approved","OVERDUE":"danger"}.get(self.status,"draft")
