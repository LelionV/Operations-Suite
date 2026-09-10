from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.conf import settings as django_settings

from .models import SystemSetting


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


EMAIL_FIELDS = [
    {'key': 'email_enabled',       'label': 'Enable Email Notifications',
     'description': 'Turn on/off all email notifications system-wide.',
     'is_password': False},
    {'key': 'email_host',          'label': 'SMTP Host',
     'description': 'e.g. smtp.gmail.com, smtp.office365.com',
     'is_password': False},
    {'key': 'email_port',          'label': 'SMTP Port',
     'description': '587 for TLS, 465 for SSL, 25 for plain.',
     'is_password': False},
    {'key': 'email_host_user',     'label': 'SMTP Username / Email',
     'description': 'The email account used to send notifications.',
     'is_password': False},
    {'key': 'email_host_password', 'label': 'SMTP Password / App Password',
     'description': 'For Gmail use an App Password, not your account password.',
     'is_password': True},
    {'key': 'email_use_tls',       'label': 'Use TLS',
     'description': 'Recommended for port 587. Set to true or false.',
     'is_password': False},
    {'key': 'email_use_ssl',       'label': 'Use SSL',
     'description': 'For port 465. Do not enable both TLS and SSL.',
     'is_password': False},
    {'key': 'email_from',          'label': 'From Email Address',
     'description': 'The sender address shown in notification emails.',
     'is_password': False},
]


def _seed_email_settings():
    """Create default SystemSetting rows if they don't exist."""
    defaults = {
        'email_enabled':       'false',
        'email_host':          '',
        'email_port':          '587',
        'email_host_user':     '',
        'email_host_password': '',
        'email_use_tls':       'true',
        'email_use_ssl':       'false',
        'email_from':          'noreply@po-system.com',
    }
    for field in EMAIL_FIELDS:
        SystemSetting.objects.get_or_create(
            key=field['key'],
            defaults={
                'label':       field['label'],
                'description': field['description'],
                'is_password': field['is_password'],
                'value':       defaults.get(field['key'], ''),
            }
        )


class EmailSettingsView(StaffRequiredMixin, TemplateView):
    template_name = 'settings_manager/email.html'

    def get(self, request, *args, **kwargs):
        _seed_email_settings()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['settings'] = SystemSetting.objects.filter(
            key__startswith='email_'
        ).order_by('key')
        ctx['email_fields'] = EMAIL_FIELDS
        ctx['field_map'] = {s.key: s for s in ctx['settings']}
        return ctx

    def post(self, request, *args, **kwargs):
        _seed_email_settings()
        for field in EMAIL_FIELDS:
            key = field['key']
            val = request.POST.get(key, '').strip()
            # For password field: only update if a value was typed
            setting = SystemSetting.objects.get(key=key)
            if field['is_password'] and not val:
                continue  # keep existing password
            setting.value = val
            setting.label       = field['label']
            setting.description = field['description']
            setting.is_password = field['is_password']
            setting.save()
        messages.success(request, 'Email settings saved.')
        return redirect(reverse_lazy('settings_manager:email'))


@login_required
def test_email(request):
    if not request.user.is_staff:
        messages.error(request, 'Staff only.')
        return redirect('/')
    if request.method == 'POST':
        to = request.POST.get('test_email_to', '').strip()
        if not to:
            messages.error(request, 'Enter a recipient email address.')
            return redirect(reverse_lazy('settings_manager:email'))
        try:
            cfg = SystemSetting.get_email_config()
            if not cfg['EMAIL_ENABLED']:
                messages.warning(request,
                    'Email is disabled in settings. Enable it first, then test.')
                return redirect(reverse_lazy('settings_manager:email'))

            # Temporarily apply DB config to Django settings for this send
            import django.core.mail as mail
            connection = mail.get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=cfg['EMAIL_HOST'],
                port=int(cfg['EMAIL_PORT'] or 587),
                username=cfg['EMAIL_HOST_USER'],
                password=cfg['EMAIL_HOST_PASSWORD'],
                use_tls=cfg['EMAIL_USE_TLS'],
                use_ssl=cfg['EMAIL_USE_SSL'],
            )
            send_mail(
                subject='[ProcureDesk] Test Email',
                message='This is a test email from ProcureDesk. Your email settings are working correctly.',
                from_email=cfg['DEFAULT_FROM_EMAIL'],
                recipient_list=[to],
                connection=connection,
            )
            messages.success(request, f'Test email sent to {to}.')
        except Exception as e:
            messages.error(request, f'Failed to send test email: {e}')
    return redirect(reverse_lazy('settings_manager:email'))
