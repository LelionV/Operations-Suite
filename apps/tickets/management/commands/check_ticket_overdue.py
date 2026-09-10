
from django.core.management.base import BaseCommand
from django.utils import timezone
class Command(BaseCommand):
    help="Send overdue ticket reminders."
    def handle(self,*args,**options):
        from apps.tickets.models import Ticket,TicketOverdue
        from apps.tickets.utils import should_send_overdue_reminder,notify_ticket,get_ticket_recipients
        active=Ticket.objects.filter(status__in=["open","in_progress"],
            expected_resolution_date__isnull=False,
            expected_resolution_date__lt=timezone.now()).select_related("created_by","department")
        count=0
        for ticket in active:
            rec,_=TicketOverdue.objects.get_or_create(ticket=ticket)
            if should_send_overdue_reminder(ticket,rec.last_notified_at):
                recipients=get_ticket_recipients(ticket)
                if ticket.department:
                    hod=ticket.department.get_hod()
                    if hod and hod.email and not any(e==hod.email for e,_ in recipients):
                        recipients.append((hod.email,hod.get_full_name()))
                try:
                    notify_ticket(ticket,event="overdue",recipients=recipients)
                    rec.mark_notified(); count+=1
                    self.stdout.write(f"  ok {ticket.code}")
                except Exception as e: self.stdout.write(f"  ! {ticket.code}: {e}")
        self.stdout.write(self.style.SUCCESS(f"Done — {count} sent."))
