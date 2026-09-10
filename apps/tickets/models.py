import os
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open',        'Open'),
        ('in_progress', 'In Progress'),
        ('resolved',    'Resolved'),
        ('closed',      'Closed'),
    ]

    code        = models.CharField(max_length=30, unique=True, editable=False)
    title       = models.CharField(max_length=255)
    description = models.TextField()

    # Assigned to a department — not an individual
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tickets',
        help_text='Department responsible for resolving this ticket.',
    )

    # Optional PO link
    purchase_order = models.ForeignKey(
        'purchase_orders.PurchaseOrder',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tickets',
        help_text='Optionally link this ticket to a Purchase Order.',
    )

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES,   default='open')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tickets_updated',
    )

    expected_resolution_date = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at   = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f'TK-{timezone.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args, **kwargs)

    def close(self):
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at'])

    def __str__(self):
        return f'{self.code} — {self.title}'

    def is_overdue(self):
        return (
            self.expected_resolution_date
            and self.status not in ('resolved', 'closed')
            and timezone.now() > self.expected_resolution_date
        )

    def overdue_days(self):
        if not self.is_overdue():
            return 0
        return (timezone.now() - self.expected_resolution_date).days

    @property
    def priority_css(self):
        return {
            'low':      'success',
            'medium':   'warning',
            'high':     'danger',
            'critical': 'proc',
        }.get(self.priority, 'draft')

    @property
    def status_css(self):
        return {
            'open':        'head',
            'in_progress': 'hod',
            'resolved':    'approved',
            'closed':      'cancelled',
        }.get(self.status, 'draft')


class TicketComment(models.Model):
    ticket     = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    sender     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='ticket_comments')
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username} @ {self.created_at:%Y-%m-%d %H:%M}'


class TicketAttachment(models.Model):
    ticket      = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file        = models.FileField(upload_to='ticket_attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, related_name='ticket_uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return f'{self.ticket.code} — {self.filename()}'


class TicketOverdue(models.Model):
    ticket             = models.OneToOneField(Ticket, on_delete=models.CASCADE,
                                               related_name='overdue_record')
    first_detected_at  = models.DateTimeField(null=True, blank=True)
    last_notified_at   = models.DateTimeField(null=True, blank=True)
    notification_count = models.PositiveIntegerField(default=0)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def mark_notified(self):
        now = timezone.now()
        if not self.first_detected_at:
            self.first_detected_at = now
        self.last_notified_at = now
        self.notification_count += 1
        self.save(update_fields=['first_detected_at', 'last_notified_at', 'notification_count'])

    def __str__(self):
        return f'Overdue: {self.ticket.code}'
