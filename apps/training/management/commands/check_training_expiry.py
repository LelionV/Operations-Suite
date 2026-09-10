
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    help="Notify employees of expiring training certifications."
    def handle(self,*args,**options):
        from apps.training.models import TrainingRecord
        from apps.notify.models import Notification
        today=timezone.now().date(); in30=today+timedelta(days=30)
        expiring=TrainingRecord.objects.filter(expiry_date__gte=today,expiry_date__lte=in30,status="COMPLETED").select_related("employee","course")
        count=0
        for rec in expiring:
            days=(rec.expiry_date-today).days
            Notification.send(rec.employee,"training",f"Training Expiring: {rec.course.title}",f"Your certification expires in {days} day(s).","/training/")
            count+=1; self.stdout.write(f"  ✓ {rec.employee} — {rec.course.title} ({days}d)")
        self.stdout.write(self.style.SUCCESS(f"Done — {count} sent."))
