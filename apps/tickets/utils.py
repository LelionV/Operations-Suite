"""
Email builders and notification sender for the ticket system.
- is_ticket_viewer users are EXCLUDED from all ticket email notifications.
- Notifications go to: ticket creator + all HODs and permissioned members of the department.
"""
from datetime import timedelta
from django.utils import timezone


def build_ticket_email(ticket, event='created', recipient_name='', ticket_url=None):
    name = recipient_name or 'Team'
    url  = ticket_url or '#'
    po_block = ''
    if ticket.purchase_order:
        po = ticket.purchase_order
        po_block = (
            f'<br><hr style="border:none;border-top:1px solid #eee">'
            f'<strong>Linked PO:</strong> {po.po_number} — {po.title} '
            f'({po.get_status_display()})<br>'
        )

    base = (
        f'<strong>Ticket:</strong> {ticket.code}<br>'
        f'<strong>Title:</strong> {ticket.title}<br>'
        f'<strong>Priority:</strong> {ticket.get_priority_display()}<br>'
        f'<strong>Status:</strong> {ticket.get_status_display()}<br>'
        f'<strong>Department:</strong> {ticket.department or "Unassigned"}<br>'
        + po_block
    )

    events = {
        'created':     ('Ticket Created',    'Your request has been logged and assigned to the department.'),
        'in_progress': ('Ticket In Progress','The department has started working on this ticket.'),
        'resolved':    ('Ticket Resolved',   'This ticket has been resolved. Please confirm and close it if satisfied.'),
        'closed':      ('Ticket Closed',     'This ticket has been closed.'),
        'updated':     ('Ticket Updated',    'This ticket has been updated.'),
        'overdue':     ('Ticket Overdue',    'This ticket is overdue. Immediate action is required.'),
    }
    title_suffix, intro = events.get(event, events['updated'])
    subject = f'[ProcureDesk] {title_suffix}: {ticket.code}'

    body = f"""
    <html><body style="font-family:Inter,Arial,sans-serif;font-size:14px;color:#1a202c">
      <p>Dear {name},</p>
      <p>{intro}</p>
      <div style="background:#f8fafc;border-left:4px solid #1B3F6E;padding:12px 16px;
                  border-radius:0 6px 6px 0;margin:16px 0">{base}</div>
      <p><a href="{url}" style="color:#1B3F6E">View Ticket</a>
         &nbsp;·&nbsp; <strong>Please do not reply to this email.</strong></p>
    </body></html>
    """
    return subject, body


def _get_smtp_connection():
    """Returns (connection, from_email) using DB-stored SMTP config, or (None, None)."""
    try:
        from apps.settings_manager.models import SystemSetting
        from django.core.mail import get_connection
        cfg = SystemSetting.get_email_config()
        if not cfg.get('EMAIL_ENABLED'):
            return None, None
        conn = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=cfg['EMAIL_HOST'],
            port=int(cfg.get('EMAIL_PORT') or 587),
            username=cfg['EMAIL_HOST_USER'],
            password=cfg['EMAIL_HOST_PASSWORD'],
            use_tls=cfg['EMAIL_USE_TLS'],
            use_ssl=cfg['EMAIL_USE_SSL'],
            fail_silently=True,
        )
        return conn, cfg.get('DEFAULT_FROM_EMAIL', 'noreply@po-system.com')
    except Exception:
        return None, None


def get_ticket_recipients(ticket):
    """
    Returns list of (email, name) for notification.

    Included:
    - Ticket creator (if they have ticket access and are NOT a ticket_viewer)
    - HODs and can_access_tickets users in the assigned department

    Excluded:
    - is_ticket_viewer users (they read-only watch, never emailed)
    - Users without ticket access
    """
    from apps.accounts.models import User

    seen = set()
    result = []

    def add(user):
        # Skip ticket viewers — they are never emailed
        if user.is_ticket_viewer:
            return
        # Must have ticket access to receive emails
        if not user.has_ticket_access():
            return
        if user.email and user.email not in seen:
            seen.add(user.email)
            result.append((user.email, user.get_full_name() or user.username))

    # Creator
    if ticket.created_by:
        add(ticket.created_by)

    # Department members with ticket access (HODs + permissioned)
    if ticket.department:
        dept_users = User.objects.filter(
            department=ticket.department,
            is_active=True,
        )
        for u in dept_users:
            add(u)

    return result


def notify_ticket(ticket, event, recipients=None, ticket_url=None):
    """Send email notifications. Skips silently if SMTP is disabled."""
    conn, from_email = _get_smtp_connection()
    if not conn:
        return
    if recipients is None:
        recipients = get_ticket_recipients(ticket)
    from django.core.mail import EmailMessage
    for email_addr, name in recipients:
        if not email_addr:
            continue
        subject, body = build_ticket_email(
            ticket, event=event, recipient_name=name, ticket_url=ticket_url)
        try:
            msg = EmailMessage(subject=subject, body=body,
                               from_email=from_email, to=[email_addr],
                               connection=conn)
            msg.content_subtype = 'html'
            msg.send(fail_silently=True)
        except Exception:
            pass


# ── Overdue helpers ─────────────────────────────────────────────────────────

def get_overdue_days(ticket):
    if not ticket.expected_resolution_date:
        return None
    return (timezone.now() - ticket.expected_resolution_date).days


def should_send_overdue_reminder(ticket, last_sent_at=None):
    if ticket.status in ('resolved', 'closed'):
        return False
    days = get_overdue_days(ticket)
    if days is None or days < 0:
        return False
    if not last_sent_at:
        return True
    if days <= 2:
        return False
    if 3 <= days <= 7:
        return timezone.now() >= last_sent_at + timedelta(days=3)
    return timezone.now() >= last_sent_at + timedelta(days=2)
