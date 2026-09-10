from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender='accounts.User')
def assign_user_permissions(sender, instance, created, **kwargs):
    """
    Automatically assign permissions based on user role flags.
    - All users get can_create_po
    - HODs additionally get can_approve_hod
    - Head approver gets can_approve_final
    """
    try:
        ct = ContentType.objects.get(app_label='accounts', model='user')
        perm_create = Permission.objects.get(content_type=ct, codename='can_create_po')
        perm_hod = Permission.objects.get(content_type=ct, codename='can_approve_hod')
        perm_head = Permission.objects.get(content_type=ct, codename='can_approve_final')
    except (ContentType.DoesNotExist, Permission.DoesNotExist):
        return

    # Everyone can create POs
    instance.user_permissions.add(perm_create)

    if instance.is_hod:
        instance.user_permissions.add(perm_hod)
    else:
        instance.user_permissions.remove(perm_hod)

    if instance.is_head_approver:
        instance.user_permissions.add(perm_head)
    else:
        instance.user_permissions.remove(perm_head)
