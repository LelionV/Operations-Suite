
from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Kind(models.TextChoices):
        # ProcureDesk kinds
        PO_SUBMITTED   = "po_submitted",   "PO Submitted"
        PO_APPROVED    = "po_approved",    "PO Approved"
        PO_REJECTED    = "po_rejected",    "PO Rejected"
        PO_ORDERED     = "po_ordered",     "PO Ordered"
        PO_DEADLINE    = "po_deadline",    "PO Deadline"
        TICKET_UPDATE  = "ticket_update",  "Ticket Update"
        TICKET_OVERDUE = "ticket_overdue", "Ticket Overdue"
        GRN_CREATED    = "grn_created",    "GRN Created"
        ASSET_UPDATE   = "asset_update",   "Asset Update"
        VISITOR        = "visitor",        "Visitor Alert"
        # OSH kinds
        EXPIRY         = "expiry",         "Certificate/PPE Expiring"
        INSPECTION     = "inspect",        "Inspection Due"
        MAINTENANCE    = "maint",          "Maintenance Due"
        TRAINING       = "training",       "Training Expiring"
        OVERDUE        = "overdue",        "Overdue Action"
        INCIDENT       = "incident",       "New Incident"
        FINDING        = "finding",        "New Finding"
        GENERAL        = "general",        "General"

    recipient  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name="notifications")
    kind       = models.CharField(max_length=30, choices=Kind.choices)
    title      = models.CharField(max_length=255)
    body       = models.TextField(blank=True)
    link       = models.CharField(max_length=500, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ["-created_at"]

    def __str__(self): return f"{self.recipient.username}: {self.title}"

    @classmethod
    def send(cls, recipient, kind, title, body="", link=""):
        if recipient:
            cls.objects.create(recipient=recipient, kind=kind,
                               title=title, body=body, link=link)

    @classmethod
    def broadcast(cls, recipients, kind, title, body="", link=""):
        for u in recipients:
            cls.send(u, kind=kind, title=title, body=body, link=link)
