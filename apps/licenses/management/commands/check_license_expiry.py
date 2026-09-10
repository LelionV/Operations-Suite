
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help="Send notifications for expiring/expired licenses and permits."
    def handle(self,*args,**options):
        from apps.licenses.models import License
        from apps.notify.models import Notification
        today=timezone.now().date()
        expiring=License.objects.filter(expiry_date__gte=today, expiry_date__lte=today+timedelta(days=30), reminder_sent=False)
        count=0
        for lic in expiring:
            days=(lic.expiry_date-today).days
            msg=f"{lic.title} expires in {days} day(s) on {lic.expiry_date}."
            if lic.responsible_person:
                Notification.send(lic.responsible_person,"expiry",f"License Expiring: {lic.title}",msg,"/licenses/")
            lic.reminder_sent=True; lic.save(update_fields=["reminder_sent"])
            count+=1; self.stdout.write(f"  ✓ {lic.title} ({days}d)")
        self.stdout.write(self.style.SUCCESS(f"Done — {count} reminders sent."))
