
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help="Notify requesters of POs approaching their submission deadline."
    def handle(self,*args,**options):
        from apps.purchase_orders.models import PurchaseOrder
        from apps.notifications.utils import notify_po_deadline
        cutoff=timezone.now()+timedelta(hours=24)
        pos=PurchaseOrder.objects.filter(
            status=PurchaseOrder.Status.DRAFT,
            submission_deadline__lte=cutoff,
            submission_deadline__isnull=False,
            deadline_notification_sent=False,
        ).select_related("requester","department")
        count=0
        for po in pos:
            try: notify_po_deadline(po); count+=1; self.stdout.write(f"  ok {po.po_number}")
            except Exception as e: self.stdout.write(f"  ! {po.po_number}: {e}")
        self.stdout.write(self.style.SUCCESS(f"Done — {count} sent."))
