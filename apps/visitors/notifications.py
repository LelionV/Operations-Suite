"""
All visitor-related notifications: in-app, email, WhatsApp.
"""
from django.utils import timezone


def _email(subject, body_html, recipients):
    try:
        from apps.settings_manager.models import SystemSetting
        from django.core.mail import get_connection, EmailMessage
        cfg = SystemSetting.get_email_config()
        if not cfg.get('EMAIL_ENABLED') or not recipients:
            return
        conn = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=cfg['EMAIL_HOST'], port=int(cfg.get('EMAIL_PORT') or 587),
            username=cfg['EMAIL_HOST_USER'], password=cfg['EMAIL_HOST_PASSWORD'],
            use_tls=cfg['EMAIL_USE_TLS'], use_ssl=cfg['EMAIL_USE_SSL'], fail_silently=True)
        msg = EmailMessage(subject=subject, body=body_html,
            from_email=cfg.get('DEFAULT_FROM_EMAIL','noreply@po-system.com'),
            to=[r for r in recipients if r], connection=conn)
        msg.content_subtype = 'html'
        msg.send(fail_silently=True)
    except Exception:
        pass


def _in_app(recipient, kind, title, body='', link=''):
    try:
        from apps.notify.models import Notification
        Notification.send(recipient, kind=kind, title=title, body=body, link=link)
    except Exception:
        pass


def _whatsapp(to_number, message):
    try:
        from .whatsapp import send_whatsapp
        send_whatsapp(to_number, message)
    except Exception:
        pass


def notify_host_on_arrival(appointment):
    """
    When gatekeeper marks ARRIVED:
    - In-app notification to host user (if in system)
    - Email to host user or dept HOD
    - WhatsApp to visitor (if phone on file)
    """
    from django.urls import reverse
    appt = appointment
    link = reverse('visitors:detail', kwargs={'pk': appt.pk})

    host = appt.host_user
    if not host and appt.host_department:
        host = appt.host_department.get_hod()

    # In-app
    if host:
        _in_app(host, 'asset_update',
            f'Visitor Arrived: {appt.visitor_name}',
            f'{appt.visitor_name} from {appt.visitor_company or "—"} has arrived at the gate.',
            link)

    # Email
    recipients = []
    if appt.host_user and appt.host_user.email:
        recipients.append(appt.host_user.email)
    elif host and host.email:
        recipients.append(host.email)

    if recipients:
        _email(
            subject=f'[ProcureDesk] Visitor Arrived: {appt.visitor_name}',
            body_html=(
                f'<p>Dear {host.get_full_name() if host else "Team"},</p>'
                f'<p>Your visitor <strong>{appt.visitor_name}</strong>'
                f'{" from "+appt.visitor_company if appt.visitor_company else ""} '
                f'has arrived at the gate.</p>'
                f'<p><strong>Appointment:</strong> {appt.ref_number}<br>'
                f'<strong>Scheduled:</strong> {appt.scheduled_date} {appt.scheduled_start}'
                f'{" — "+str(appt.scheduled_end) if appt.scheduled_end else ""}<br>'
                f'{"<strong>Agenda:</strong> "+appt.agenda+"<br>" if appt.agenda else ""}'
                f'{"<strong>Vehicle:</strong> "+appt.vehicle_plate+" "+appt.vehicle_make if appt.vehicle_plate else ""}</p>'
                f'<p>Please proceed to receive your visitor.</p>'
            ),
            recipients=recipients,
        )

    # WhatsApp to visitor
    if appt.visitor_phone:
        msg = (
            f'Hello {appt.visitor_name},\n\n'
            f'You have been checked in at the gate.\n'
            f'Appointment Ref: {appt.ref_number}\n'
            f'Your host has been notified and will receive you shortly.\n\n'
            f'Thank you for visiting.'
        )
        _whatsapp(appt.visitor_phone, msg)

    appointment.host_notified_at = timezone.now()
    appointment.arrival_whatsapp_sent = bool(appt.visitor_phone)
    appointment.save(update_fields=['host_notified_at', 'arrival_whatsapp_sent'])


def notify_appointment_booked(appointment):
    """Confirm appointment to host and visitor when created."""
    appt = appointment
    from django.urls import reverse
    link = reverse('visitors:detail', kwargs={'pk': appt.pk})

    host = appt.host_user
    if not host and appt.host_department:
        host = appt.host_department.get_hod()

    if host:
        _in_app(host, 'asset_update',
            f'New Appointment: {appt.visitor_name}',
            f'Scheduled {appt.scheduled_date} at {appt.scheduled_start}',
            link)
        if host.email:
            _email(
                subject=f'[ProcureDesk] Appointment Booked: {appt.visitor_name} — {appt.ref_number}',
                body_html=(
                    f'<p>Dear {host.get_full_name()},</p>'
                    f'<p>A visitor appointment has been booked for you.</p>'
                    f'<p><strong>Visitor:</strong> {appt.visitor_name}'
                    f'{" — "+appt.visitor_company if appt.visitor_company else ""}<br>'
                    f'<strong>Date:</strong> {appt.scheduled_date}<br>'
                    f'<strong>Time:</strong> {appt.scheduled_start}'
                    f'{" — "+str(appt.scheduled_end) if appt.scheduled_end else ""}<br>'
                    f'{"<strong>Agenda:</strong> "+appt.agenda if appt.agenda else ""}</p>'
                    f'<p>Ref: {appt.ref_number}</p>'
                ),
                recipients=[host.email],
            )

    # WhatsApp confirmation to visitor
    if appt.visitor_phone:
        msg = (
            f'Dear {appt.visitor_name},\n\n'
            f'Your appointment has been confirmed.\n\n'
            f'Ref: {appt.ref_number}\n'
            f'Date: {appt.scheduled_date}\n'
            f'Time: {appt.scheduled_start}'
            + (f' — {appt.scheduled_end}' if appt.scheduled_end else '') + '\n'
            + (f'Host: {host.get_full_name()}' if host else '') + '\n\n'
            f'Please bring a valid ID on arrival.\nThank you.'
        )
        _whatsapp(appt.visitor_phone, msg)


def notify_appointment_cancelled(appointment):
    appt = appointment
    host = appt.host_user
    if not host and appt.host_department:
        host = appt.host_department.get_hod()

    if appt.visitor_phone:
        msg = (
            f'Dear {appt.visitor_name},\n\n'
            f'Your appointment (Ref: {appt.ref_number}) on {appt.scheduled_date} '
            f'at {appt.scheduled_start} has been cancelled.\n\n'
            f'Please contact the office for more information.'
        )
        _whatsapp(appt.visitor_phone, msg)
