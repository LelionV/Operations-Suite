
from django.contrib.auth.models import AbstractUser
from django.db import models


class Site(models.Model):
    """Physical site / location. Used by OSH modules."""
    name      = models.CharField(max_length=200)
    code      = models.CharField(max_length=20, unique=True)
    address   = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ["name"]
    def __str__(self): return self.name


class User(AbstractUser):
    """
    Unified user model for ProcureDesk + OSH.
    ProcureDesk roles are boolean flags (is_hod, is_head_approver, …).
    OSH role is a single choice field used for EHS module access.
    """
    class OSHRole(models.TextChoices):
        NONE     = "",        "No OSH Role"
        ADMIN    = "admin",   "OSH Admin"
        MANAGER  = "manager", "HSE Manager"
        OFFICER  = "officer", "HSE Officer"
        AUDITOR  = "auditor", "Auditor"
        EMPLOYEE = "employee","Employee"
        VIEWER   = "viewer",  "Read-Only Viewer"

    # ── Shared ──────────────────────────────────────────────────────────
    department   = models.ForeignKey(
        "departments.Department", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="members")
    site         = models.ForeignKey(
        Site, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    job_title    = models.CharField(max_length=200, blank=True)
    phone        = models.CharField(max_length=30, blank=True)
    employee_id  = models.CharField(max_length=50, blank=True)

    # ── ProcureDesk role flags ───────────────────────────────────────────
    is_hod                 = models.BooleanField(default=False)
    is_head_approver       = models.BooleanField(default=False)
    is_procurement_officer = models.BooleanField(default=False)
    is_storekeeper         = models.BooleanField(default=False)
    is_stock_manager       = models.BooleanField(default=False)
    is_asset_manager       = models.BooleanField(default=False)
    can_access_tickets     = models.BooleanField(default=False)
    is_gatekeeper          = models.BooleanField(default=False)
    is_ticket_viewer       = models.BooleanField(default=False)

    # ── OSH role ─────────────────────────────────────────────────────────
    osh_role = models.CharField(
        max_length=20, choices=OSHRole.choices, default=OSHRole.NONE, blank=True,
        verbose_name="OSH Role",
        help_text="Role within the OSH / EHS compliance module.")

    class Meta:
        permissions = [
            ("can_create_po",    "Can create purchase order"),
            ("can_approve_hod",  "Can approve as HOD"),
            ("can_approve_final","Can give final head approval"),
        ]

    # ── Helpers — ProcureDesk ────────────────────────────────────────────
    def has_ticket_access(self):
        return (self.is_hod or self.is_ticket_viewer or self.is_staff
                or self.is_head_approver or self.can_access_tickets)

    # ── Helpers — OSH ────────────────────────────────────────────────────
    def is_hse_manager(self):
        return self.osh_role in ("admin","manager") or self.is_staff

    def is_hse_officer(self):
        return self.osh_role in ("admin","manager","officer") or self.is_staff

    def is_auditor_osh(self):
        return self.osh_role in ("admin","manager","auditor") or self.is_staff

    def can_manage_osh(self):
        return self.osh_role in ("admin","manager","officer") or self.is_staff

    def get_role_display(self):
        """Display string combining both role systems."""
        flags = []
        if self.is_head_approver:       flags.append("Head Approver")
        if self.is_hod:                 flags.append("HOD")
        if self.is_procurement_officer: flags.append("Procurement")
        if self.is_storekeeper:         flags.append("Storekeeper")
        if self.is_stock_manager:       flags.append("Stock Mgr")
        if self.is_asset_manager:       flags.append("Asset Mgr")
        if self.is_gatekeeper:          flags.append("Gatekeeper")
        if self.is_ticket_viewer:       flags.append("Ticket Viewer")
        if self.osh_role:               flags.append(self.get_osh_role_display())
        return " · ".join(flags) if flags else "User"

    def __str__(self):
        return f"{self.get_full_name() or self.username} [{self.get_role_display()}]"
