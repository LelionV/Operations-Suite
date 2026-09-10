from django.db import models
from django.contrib.auth.models import Group


class Department(models.Model):
    site = models.ForeignKey("accounts.Site", null=True, blank=True, on_delete=models.SET_NULL, related_name="departments")
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=10, unique=True)
    group = models.OneToOneField(
        Group,
        on_delete=models.PROTECT,
        related_name='department',
        help_text='Django Group that maps to this department.',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'

    def get_hod(self):
        """Return the HOD user for this department, or None."""
        return self.members.filter(is_hod=True, is_active=True).first()
