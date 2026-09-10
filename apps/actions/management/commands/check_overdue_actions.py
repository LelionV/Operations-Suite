
from django.core.management.base import BaseCommand
from django.utils import timezone
class Command(BaseCommand):
    help="Notify action owners of overdue CAPA actions."
    def handle(self,*args,**options):
        from apps.actions.models import Action
        from apps.notify.models import Notification
        today=timezone.now().date()
        overdue=[a for a in Action.objects.filter(status__in=["OPEN","IN_PROGRESS"],due_date__lt=today).select_related("owner") if a.owner]
        count=0
        for a in overdue:
            Notification.send(a.owner,"overdue",f"Overdue Action: {a.title}",f"Action was due {a.due_date}. Please update.","/actions/")
            count+=1; self.stdout.write(f"  ✓ {a.title} (owner: {a.owner})")
        self.stdout.write(self.style.SUCCESS(f"Done — {count} notified."))
