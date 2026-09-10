from django.db import models
from django.conf import settings
from decimal import Decimal, InvalidOperation

MONTH_FIELDS = ['usage_jun','usage_jul','usage_aug','usage_sep','usage_oct','usage_nov',
                'usage_dec','usage_jan','usage_feb','usage_mar','usage_apr','usage_may']

class StockItem(models.Model):
    class Sourcing(models.TextChoices):
        LOCAL  = 'LOCAL',  'Local'
        IMPORT = 'IMPORT', 'Import'

    qb_code          = models.CharField(max_length=100, unique=True)
    description      = models.CharField(max_length=255)
    uom              = models.CharField(max_length=50)
    sourcing         = models.CharField(max_length=10, choices=Sourcing.choices, blank=True, default='')
    stock_required   = models.BooleanField(default=True)
    purchase_pattern = models.CharField(max_length=10, blank=True, default='ONGOING')
    category         = models.CharField(max_length=100, blank=True)
    lead_time_months = models.DecimalField(max_digits=4, decimal_places=1, default=3)
    current_stock    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    open_order       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_jun = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_jul = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_aug = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_sep = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_oct = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_nov = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_dec = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_jan = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_feb = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_mar = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_apr = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    usage_may = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    to_order  = models.BooleanField(default=False)
    order_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['qb_code']

    def __str__(self):
        return f'{self.qb_code} — {self.description}'

    @property
    def monthly_usages(self):
        return [float(getattr(self, f)) for f in MONTH_FIELDS]

    @property
    def non_zero_months(self):
        return [u for u in self.monthly_usages if u > 0]

    @property
    def monthly_moving_average(self):
        nz = self.non_zero_months
        return round(sum(nz)/len(nz), 2) if nz else 0

    @property
    def annual_usage(self):
        return round(sum(self.monthly_usages), 2)

    @property
    def stock_cover_months(self):
        avg = self.monthly_moving_average
        return round(float(self.current_stock)/avg, 2) if avg else None

    @property
    def min_threshold(self):
        return round(float(self.lead_time_months) * self.monthly_moving_average, 2)

    @property
    def max_threshold(self):
        return self.annual_usage

    @property
    def target_reorder_value(self):
        v = self.max_threshold - float(self.current_stock) - float(self.open_order)
        return round(max(v, 0), 2)

    @property
    def action(self):
        avg = self.monthly_moving_average
        if avg == 0:
            return 'NO USAGE DATA'
        stock = float(self.current_stock)
        if stock <= 0:
            return 'OUT OF STOCK'
        if stock > self.max_threshold:
            return 'OVERSTOCKED'
        if stock <= self.min_threshold:
            return 'REORDER NOW'
        cover = self.stock_cover_months or 0
        if cover <= float(self.lead_time_months):
            return 'REORDER SOON'
        return 'WELL STOCKED'

    @property
    def action_css(self):
        return {'OUT OF STOCK':'danger','REORDER NOW':'danger','REORDER SOON':'warning',
                'OVERSTOCKED':'info','WELL STOCKED':'success'}.get(self.action,'muted')


class StockUploadLog(models.Model):
    filename     = models.CharField(max_length=255)
    uploaded_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    rows_total   = models.IntegerField(default=0)
    rows_created = models.IntegerField(default=0)
    rows_updated = models.IntegerField(default=0)
    rows_skipped = models.IntegerField(default=0)
    notes        = models.TextField(blank=True)
    uploaded_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
