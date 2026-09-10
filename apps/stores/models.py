from django.db import models
from django.conf import settings


class GoodsReceivedNote(models.Model):
    class GRNStatus(models.TextChoices):
        PARTIAL  = 'PARTIAL',  'Partially Received'
        COMPLETE = 'COMPLETE', 'Fully Received'

    purchase_order = models.OneToOneField(
        'purchase_orders.PurchaseOrder',
        on_delete=models.PROTECT, related_name='grn')
    grn_number  = models.CharField(max_length=30, unique=True, editable=False)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='grns_received')
    received_at = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=20, choices=GRNStatus.choices,
                                   default=GRNStatus.PARTIAL)
    notes       = models.TextField(blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Goods Received Note'
        verbose_name_plural = 'Goods Received Notes'

    def save(self, *args, **kwargs):
        if not self.grn_number:
            from django.utils import timezone
            import uuid
            self.grn_number = f'GRN-{timezone.now().strftime("%Y%m")}-{str(uuid.uuid4()).upper()[:6]}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.grn_number} — {self.purchase_order.po_number}'

    def refresh_status(self):
        all_ok = all(item.is_fully_received for item in self.grn_items.all())
        self.status = self.GRNStatus.COMPLETE if all_ok else self.GRNStatus.PARTIAL
        self.save(update_fields=['status'])


class GRNLineItem(models.Model):
    grn          = models.ForeignKey(GoodsReceivedNote, on_delete=models.CASCADE,
                                     related_name='grn_items')
    po_line_item = models.OneToOneField('purchase_orders.POLineItem',
                                        on_delete=models.PROTECT, related_name='grn_line')
    qty_received = models.PositiveIntegerField(default=0)
    condition    = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)

    class Meta:
        ordering = ['pk']

    @property
    def qty_ordered(self):    return self.po_line_item.quantity
    @property
    def qty_outstanding(self): return max(0, self.qty_ordered - self.qty_received)
    @property
    def is_fully_received(self): return self.qty_received >= self.qty_ordered
    @property
    def code(self):        return self.po_line_item.code
    @property
    def description(self): return self.po_line_item.description
    @property
    def uom(self):         return self.po_line_item.uom

    def __str__(self):
        return f'{self.code}: {self.qty_received}/{self.qty_ordered}'
