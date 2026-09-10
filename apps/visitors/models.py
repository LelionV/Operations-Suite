import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class WhatsAppConfig(models.Model):
    """
    Stores WhatsApp Business API credentials.
    Only one row is active at a time.
    Configured via /system/whatsapp/ by staff.
    """
    name         = models.CharField(max_length=100, default='Default')
    provider     = models.CharField(max_length=20, default='twilio',
        choices=[('twilio','Twilio'),('meta','Meta Cloud API'),('custom','Custom REST')])
    # Twilio / Meta shared fields
    account_sid  = models.CharField(max_length=200, blank=True, help_text='Twilio Account SID or Meta WABA ID')
    auth_token   = models.CharField(max_length=200, blank=True, help_text='Twilio Auth Token or Meta API Token')
    from_number  = models.CharField(max_length=30, blank=True, help_text='WhatsApp sender number e.g. +12345678900')
    # Custom REST
    api_url      = models.CharField(max_length=500, blank=True, help_text='Custom REST endpoint URL')
    api_key      = models.CharField(max_length=300, blank=True)
    extra_headers= models.TextField(blank=True, help_text='JSON dict of extra headers for custom provider')
    is_active    = models.BooleanField(default=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'WhatsApp Configuration'

    def save(self, *args, **kwargs):
        if self.is_active:
            WhatsAppConfig.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.provider})'


class VisitorAppointment(models.Model):
    """
    An appointment booked for a visitor, either by a staff member
    (who is expecting the visitor) or by the gatekeeper (walk-in).
    """
    class Status(models.TextChoices):
        SCHEDULED  = 'SCHEDULED',  'Scheduled'
        ARRIVED    = 'ARRIVED',    'Arrived'
        IN_MEETING = 'IN_MEETING', 'In Meeting'
        COMPLETED  = 'COMPLETED',  'Completed'
        CANCELLED  = 'CANCELLED',  'Cancelled'
        NO_SHOW    = 'NO_SHOW',    'No Show'

    ref_number = models.CharField(max_length=20, unique=True, editable=False)

    # Visitor info
    visitor_name       = models.CharField(max_length=255)
    visitor_email      = models.EmailField(blank=True)
    visitor_phone      = models.CharField(max_length=30, blank=True,
        help_text='WhatsApp-capable number e.g. +254712345678')
    visitor_company    = models.CharField(max_length=255, blank=True)
    visitor_id_number  = models.CharField(max_length=100, blank=True,
        help_text='National ID / Passport number')

    # Who they are visiting
    host_user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='visitor_appointments',
        help_text='Staff member being visited. Leave blank if unknown — department HOD will be notified.')
    host_department = models.ForeignKey(
        'departments.Department', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='visitor_appointments',
        help_text='Department being visited (used if host user is not in system).')

    # Scheduling
    scheduled_date  = models.DateField()
    scheduled_start = models.TimeField()
    scheduled_end   = models.TimeField(null=True, blank=True,
        help_text='Expected end time (optional).')
    agenda          = models.TextField(blank=True,
        help_text='Purpose of visit / meeting agenda (optional).')

    # Vehicle(s)
    vehicle_plate   = models.CharField(max_length=50, blank=True,
        help_text='e.g. KCA 001A')
    vehicle_make    = models.CharField(max_length=100, blank=True,
        help_text='e.g. Toyota Prado')
    vehicle_colour  = models.CharField(max_length=50, blank=True)

    # Status
    status      = models.CharField(max_length=20, choices=Status.choices,
                                    default=Status.SCHEDULED)
    booked_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='bookings_made',
        help_text='User who created this appointment.')
    notes       = models.TextField(blank=True)

    # Arrival tracking
    arrived_at      = models.DateTimeField(null=True, blank=True)
    checked_out_at  = models.DateTimeField(null=True, blank=True)
    badge_number    = models.CharField(max_length=20, blank=True)

    # Notification tracking
    host_notified_at    = models.DateTimeField(null=True, blank=True)
    arrival_whatsapp_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_start']

    def save(self, *args, **kwargs):
        if not self.ref_number:
            self.ref_number = f'VIS-{timezone.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:5].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ref_number} — {self.visitor_name}'

    @property
    def status_css(self):
        return {
            'SCHEDULED':  'head',
            'ARRIVED':    'hod',
            'IN_MEETING': 'proc',
            'COMPLETED':  'approved',
            'CANCELLED':  'cancelled',
            'NO_SHOW':    'rejected',
        }.get(self.status, 'draft')

    @property
    def host_display(self):
        if self.host_user:
            return self.host_user.get_full_name() or self.host_user.username
        if self.host_department:
            return f'{self.host_department.name} (Department)'
        return '—'

    @property
    def is_today(self):
        return self.scheduled_date == timezone.now().date()


class VisitorLog(models.Model):
    """Append-only log of every status change on an appointment."""
    appointment = models.ForeignKey(VisitorAppointment, on_delete=models.CASCADE,
                                     related_name='logs')
    actor       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL)
    from_status = models.CharField(max_length=20, blank=True)
    to_status   = models.CharField(max_length=20)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.appointment.ref_number}: {self.from_status} → {self.to_status}'
