
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help="Flag expiring PPE items."
    def handle(self,*args,**options):
        from apps.ppe.models import PPEItem
        today=timezone.now().date(); in30=today+timedelta(days=30)
        expiring=PPEItem.objects.filter(expiry_date__gte=today,expiry_date__lte=in30,status="ISSUED")
        for item in expiring:
            days=(item.expiry_date-today).days
            self.stdout.write(f"  PPE expiring: {item.item_code} — {item.ppe_type} ({days}d) — {item.issued_to}")
        self.stdout.write(self.style.SUCCESS(f"Done — {expiring.count()} items flagged."))
