import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_po_number():
    prefix = timezone.now().strftime('%Y%m')
    uid = str(uuid.uuid4()).upper()[:6]
    return f'PO-{prefix}-{uid}'


class PurchaseOrder(models.Model):

    class Status(models.TextChoices):
        DRAFT        = 'DRAFT',        'Draft'
        PENDING_HOD  = 'PENDING_HOD',  'Pending HOD Approval'
        PENDING_HEAD = 'PENDING_HEAD', 'Pending Head Approval'
        APPROVED     = 'APPROVED',     'Approved'
        SENT_PROC    = 'SENT_PROC',    'Sent to Procurement'
        ORDERED      = 'ORDERED',      'Ordered'
        RECEIVED     = 'RECEIVED',     'Received by Stores'
        REJECTED     = 'REJECTED',     'Rejected'
        CANCELLED    = 'CANCELLED',    'Cancelled'

    po_number    = models.CharField(max_length=30, unique=True, editable=False)
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    department   = models.ForeignKey(
        'departments.Department', on_delete=models.PROTECT, related_name='purchase_orders')
    requester    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='requested_pos')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # HOD approval
    hod_approver    = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='hod_approvals')
    hod_approved_at = models.DateTimeField(null=True, blank=True)
    hod_auto        = models.BooleanField(default=False)

    # Head approval
    head_approver    = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='head_approvals')
    head_approved_at = models.DateTimeField(null=True, blank=True)

    # Procurement
    procurement_officer    = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='procurement_pos')
    sent_to_procurement_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)
    signature_requester    = models.TextField(blank=True)
    signature_requester_at = models.DateTimeField(null=True,blank=True)
    signature_hod          = models.TextField(blank=True)
    signature_hod_at       = models.DateTimeField(null=True,blank=True)
    signature_head         = models.TextField(blank=True)
    signature_head_at      = models.DateTimeField(null=True,blank=True)
    submission_deadline        = models.DateTimeField(null=True,blank=True)
    deadline_notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.po_number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = generate_po_number()
        super().save(*args, **kwargs)

    def recalculate_total(self):
        total = sum(item.total_price for item in self.line_items.filter(is_rejected=False))
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    # ── Permission helpers ────────────────────────────────────────────

    def is_editable_by(self, user):
        return self.status == self.Status.DRAFT and self.requester == user

    def can_be_submitted_by(self, user):
        return self.status == self.Status.DRAFT and self.requester == user

    def can_be_hod_approved_by(self, user):
        return (
            self.status == self.Status.PENDING_HOD
            and user.is_hod
            and user.department == self.department
            and self.requester != user
        )

    def can_be_head_approved_by(self, user):
        # Must be PENDING_HEAD AND HOD must already have approved
        return (
            self.status == self.Status.PENDING_HEAD
            and user.is_head_approver
            and self.hod_approver is not None
        )

    def can_reject_items_as(self, user):
        if self.status == self.Status.PENDING_HOD:
            return user.is_hod and user.department == self.department
        if self.status == self.Status.PENDING_HEAD:
            return user.is_head_approver
        return False

    def can_be_rejected_by(self, user):
        # Rejection only allowed at active approval stages
        if self.status == self.Status.PENDING_HOD:
            return user.is_hod and user.department == self.department
        if self.status == self.Status.PENDING_HEAD:
            return user.is_head_approver
        return False

    def can_be_cancelled_by(self, user):
        return (
            self.status in (self.Status.DRAFT, self.Status.PENDING_HOD, self.Status.PENDING_HEAD)
            and (self.requester == user or user.is_staff)
        )

    @property
    def active_line_items(self):
        return self.line_items.filter(is_rejected=False)

    @property
    def rejected_line_items(self):
        return self.line_items.filter(is_rejected=True)

    @property
    def status_badge(self):
        return {
            'DRAFT':        'secondary',
            'PENDING_HOD':  'warning',
            'PENDING_HEAD': 'info',
            'APPROVED':     'success',
            'SENT_PROC':    'primary',
            'ORDERED':      'primary',
            'RECEIVED':     'success',
            'REJECTED':     'danger',
            'CANCELLED':    'dark',
        }.get(self.status, 'secondary')

    @property
    def workflow_step(self):
        """Returns (current_step_index, total_steps) for progress display."""
        steps = ['DRAFT','PENDING_HOD','PENDING_HEAD','SENT_PROC','ORDERED','RECEIVED']
        try:
            return steps.index(self.status)
        except ValueError:
            return 0


class POLineItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    qb_item     = models.ForeignKey('inventory.QBItem', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='po_line_items')
    code        = models.CharField(max_length=100, verbose_name='Item Code')
    description = models.CharField(max_length=255, verbose_name='Item Description')
    uom         = models.CharField(max_length=50,  verbose_name='Unit of Measure')
    spec        = models.TextField(blank=True, verbose_name='Specification')
    quantity    = models.PositiveIntegerField(default=1)
    purpose     = models.TextField(blank=True)
    photo       = models.ImageField(upload_to='po_photos/', null=True, blank=True)
    lead_time   = models.CharField(max_length=100, blank=True)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)

    is_rejected      = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    rejected_by      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rejected_line_items')
    rejected_at = models.DateTimeField(null=True, blank=True)

    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'pk']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase_order.recalculate_total()

    def delete(self, *args, **kwargs):
        po = self.purchase_order
        super().delete(*args, **kwargs)
        po.recalculate_total()

    def __str__(self):
        return f'{self.code} — {self.description} × {self.quantity}'


class ApprovalLog(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='logs')
    actor          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    from_status    = models.CharField(max_length=20)
    to_status      = models.CharField(max_length=20)
    comment        = models.TextField(blank=True)
    affected_items = models.ManyToManyField(POLineItem, blank=True, related_name='log_entries')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.purchase_order.po_number}: {self.from_status}→{self.to_status}'
