
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help="Notify inspectors of upcoming and overdue inspections."
    def handle(self,*args,**options):
        from apps.inspections.models import Inspection
        from apps.notify.models import Notification
        today=timezone.now().date(); in7=today+timedelta(days=7)
        due=Inspection.objects.filter(scheduled_date__lte=in7,scheduled_date__gte=today,status="SCHEDULED").select_related("inspector")
        for insp in due:
            if insp.inspector:
                days=(insp.scheduled_date-today).days
                Notification.send(insp.inspector,"inspect",f"Inspection Due: {insp.title}",f"Scheduled for {insp.scheduled_date} ({days}d).","/inspections/")
            self.stdout.write(f"  Due: {insp.title} ({insp.scheduled_date})")
        overdue=Inspection.objects.filter(scheduled_date__lt=today,status="SCHEDULED").select_related("inspector")
        for insp in overdue:
            if insp.inspector:
                Notification.send(insp.inspector,"inspect",f"Overdue Inspection: {insp.title}",f"Was due {insp.scheduled_date}.","/inspections/")
            self.stdout.write(f"  Overdue: {insp.title}")
        self.stdout.write(self.style.SUCCESS("Done."))
