
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help="Notify of overdue equipment inspections and maintenance."
    def handle(self,*args,**options):
        from apps.equipment.models import Equipment
        from apps.notify.models import Notification
        today=timezone.now().date()
        insp_overdue=Equipment.objects.filter(next_inspection__lt=today,status="OPERATIONAL")
        for eq in insp_overdue:
            if eq.responsible_person:
                Notification.send(eq.responsible_person,"inspect",f"Inspection Overdue: {eq.name}",f"{eq.asset_id} inspection was due {eq.next_inspection}.","/equipment/")
            self.stdout.write(f"  Insp overdue: {eq.asset_id} — {eq.name}")
        maint_overdue=Equipment.objects.filter(next_maintenance__lt=today,status="OPERATIONAL")
        for eq in maint_overdue:
            if eq.responsible_person:
                Notification.send(eq.responsible_person,"maint",f"Maintenance Overdue: {eq.name}",f"{eq.asset_id} maintenance was due {eq.next_maintenance}.","/equipment/")
            self.stdout.write(f"  Maint overdue: {eq.asset_id} — {eq.name}")
        self.stdout.write(self.style.SUCCESS(f"Done."))
