from django.db import models
from django.conf import settings


class ProcurementOrder(models.Model):
    class OrderStatus(models.TextChoices):
        OPEN    = 'OPEN',    'Open'
        ORDERED = 'ORDERED', 'Ordered — Sent to Stores'

    purchase_order = models.OneToOneField(
        'purchase_orders.PurchaseOrder',
        on_delete=models.PROTECT,
        related_name='procurement_order',
    )
    # All optional — procurement officer fills what they know
    supplier_name    = models.CharField(max_length=255, blank=True)
    supplier_contact = models.CharField(max_length=255, blank=True)
    supplier_email   = models.EmailField(blank=True)
    order_reference  = models.CharField(max_length=100, blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    notes            = models.TextField(blank=True)

    status     = models.CharField(max_length=20, choices=OrderStatus.choices,
                                  default=OrderStatus.OPEN)
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='procurement_orders_placed')
    ordered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Procurement: {self.purchase_order.po_number}'


class ProcurementLineItem(models.Model):
    procurement_order = models.ForeignKey(
        ProcurementOrder, on_delete=models.CASCADE, related_name='proc_line_items')
    po_line_item = models.OneToOneField(
        'purchase_orders.POLineItem', on_delete=models.PROTECT,
        related_name='procurement_line')
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)
    notes       = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.po_line_item.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def code(self): return self.po_line_item.code
    @property
    def description(self): return self.po_line_item.description
    @property
    def uom(self): return self.po_line_item.uom
    @property
    def quantity(self): return self.po_line_item.quantity

    def __str__(self):
        return f'{self.po_line_item.code} @ {self.unit_price}'
