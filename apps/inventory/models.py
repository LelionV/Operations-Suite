from django.db import models
from django.conf import settings


class QBItem(models.Model):
    """
    Items imported from QuickBooks.
    code        = QB item code (used as the item identifier on PO line items)
    name        = QB item description (shown as 'Description' on forms)
    uom         = Unit of Measure as exported from QB
    is_active   = soft-delete so old items don't break existing POs
    """
    code      = models.CharField(max_length=100, unique=True)
    name      = models.CharField(max_length=255)
    uom       = models.CharField(max_length=50, verbose_name='Unit of Measure')
    is_active = models.BooleanField(default=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, on_delete=models.SET_NULL,
        related_name='qb_uploads',
    )
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'QB Item'
        verbose_name_plural = 'QB Items'

    def __str__(self):
        return f'{self.code} — {self.name} [{self.uom}]'


class QBUploadLog(models.Model):
    """Record of every QB import batch."""
    uploaded_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, on_delete=models.SET_NULL,
    )
    uploaded_at   = models.DateTimeField(auto_now_add=True)
    filename      = models.CharField(max_length=255)
    rows_total    = models.PositiveIntegerField(default=0)
    rows_created  = models.PositiveIntegerField(default=0)
    rows_updated  = models.PositiveIntegerField(default=0)
    rows_skipped  = models.PositiveIntegerField(default=0)
    notes         = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.filename} @ {self.uploaded_at:%Y-%m-%d %H:%M}'
