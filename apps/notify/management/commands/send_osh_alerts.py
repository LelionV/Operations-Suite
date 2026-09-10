
"""
python manage.py send_osh_alerts
Run daily via cron at 07:00.
Sends in-app notifications for all expiry / overdue OSH events.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = "Send OSH daily alert notifications."

    def handle(self, *args, **options):
        today = timezone.now().date()
        in_30 = today + timezone.timedelta(days=30)
        in_7  = today + timezone.timedelta(days=7)
        count = 0
        from apps.notify.models import Notification

        def notify(recipients, kind, title, body="", link=""):
            nonlocal count
            for u in (recipients if hasattr(recipients,"__iter__") else [recipients]):
                if u: Notification.send(u, kind=kind, title=title, body=body, link=link); count+=1

        def managers():
            from apps.accounts.models import User
            return list(User.objects.filter(osh_role__in=["admin","manager","officer"],is_active=True))

        mgrs = managers()

        # Licenses expiring
        from apps.licenses.models import License
        for lic in License.objects.filter(expiry_date__lte=in_30,expiry_date__gte=today,reminder_sent=False):
            days=(lic.expiry_date-today).days
            notify(mgrs,"expiry",f"License Expiring: {lic.title}",f"Expires in {days} days on {lic.expiry_date}.")
            lic.reminder_sent=True; lic.save(update_fields=["reminder_sent"])
            self.stdout.write(f"  License: {lic.title}")

        # Equipment inspection overdue
        from apps.equipment.models import Equipment
        for eq in Equipment.objects.filter(next_inspection__lte=in_7,status="OPERATIONAL"):
            if eq.inspection_overdue:
                notify(mgrs,"inspect",f"Inspection Overdue: {eq.name}",f"Due: {eq.next_inspection}")
                self.stdout.write(f"  Inspection: {eq.asset_id}")

        # Equipment maintenance overdue
        for eq in Equipment.objects.filter(next_maintenance__lte=in_7,status="OPERATIONAL"):
            if eq.maintenance_overdue:
                notify(mgrs,"maint",f"Maintenance Overdue: {eq.name}",f"Due: {eq.next_maintenance}")
                self.stdout.write(f"  Maintenance: {eq.asset_id}")

        # PPE expiring
        from apps.ppe.models import PPEItem
        for ppe in PPEItem.objects.filter(expiry_date__lte=in_30,expiry_date__gte=today):
            notify(mgrs,"expiry",f"PPE Expiring: {ppe.item_code} ({ppe.ppe_type})",f"Expires {ppe.expiry_date}.")
            self.stdout.write(f"  PPE: {ppe.item_code}")

        # Training expiring
        from apps.training.models import TrainingRecord
        for tr in TrainingRecord.objects.filter(expiry_date__lte=in_30,expiry_date__gte=today,status="COMPLETED"):
            notify([tr.employee]+mgrs,"training",
                f"Training Expiring: {tr.course.title}",
                f"Expires {tr.expiry_date} — {tr.employee.get_full_name()}")
            self.stdout.write(f"  Training: {tr.employee} — {tr.course}")

        # Overdue CAPA
        from apps.actions.models import Action
        for a in Action.objects.filter(status__in=["OPEN","IN_PROGRESS"]).select_related("owner"):
            if a.is_overdue:
                recips=[a.owner]+mgrs if a.owner else mgrs
                notify(recips,"overdue",f"Overdue Action: {a.title}",f"Due {a.due_date}.")
                a.status="OVERDUE"; a.save(update_fields=["status"])
                self.stdout.write(f"  CAPA overdue: {a.title}")

        # Overdue NC
        from apps.nonconformities.models import NonConformity
        for nc in NonConformity.objects.filter(status__in=["OPEN","IN_PROGRESS"]).select_related("responsible_person"):
            if nc.is_overdue:
                recips=[nc.responsible_person]+mgrs if nc.responsible_person else mgrs
                notify(recips,"overdue",f"Overdue NC: {nc.title}",f"Due {nc.due_date}.")
                self.stdout.write(f"  NC overdue: {nc.title}")

        # Upcoming audits
        from apps.audits.models import Audit
        for audit in Audit.objects.filter(status="PLANNED",scheduled_date__lte=in_7,scheduled_date__gte=today):
            notify(mgrs,"general",f"Upcoming Audit: {audit.title}",f"Scheduled {audit.scheduled_date}.")
            self.stdout.write(f"  Audit: {audit.title}")

        self.stdout.write(self.style.SUCCESS(f"Done — {count} notification(s) sent."))
