from django.db import models


class SystemSetting(models.Model):
    """
    Key-value store for system-wide settings.
    Email config is stored here so admins can update without touching code.
    """
    key         = models.CharField(max_length=100, unique=True)
    value       = models.TextField(blank=True)
    label       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_password = models.BooleanField(default=False, help_text='Render as password field in UI')
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return self.label

    @classmethod
    def get(cls, key, default=''):
        try:
            return cls.objects.get(key=key).value or default
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_email_config(cls):
        return {
            'EMAIL_HOST':          cls.get('email_host', ''),
            'EMAIL_PORT':          cls.get('email_port', '587'),
            'EMAIL_HOST_USER':     cls.get('email_host_user', ''),
            'EMAIL_HOST_PASSWORD': cls.get('email_host_password', ''),
            'EMAIL_USE_TLS':       cls.get('email_use_tls', 'true').lower() == 'true',
            'EMAIL_USE_SSL':       cls.get('email_use_ssl', 'false').lower() == 'true',
            'DEFAULT_FROM_EMAIL':  cls.get('email_from', 'noreply@po-system.com'),
            'EMAIL_ENABLED':       cls.get('email_enabled', 'false').lower() == 'true',
        }
