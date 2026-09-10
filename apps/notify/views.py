from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification
@login_required
def notification_list(request):
    notes=list(Notification.objects.filter(recipient=request.user)[:40])
    return JsonResponse({"notifications":[{"id":n.pk,"kind":n.kind,"title":n.title,"body":n.body,
        "link":n.link,"is_read":n.is_read,"created_at":n.created_at.strftime("%d %b %Y %H:%M")}
        for n in notes],"unread":Notification.objects.filter(recipient=request.user,is_read=False).count()})
@login_required
def unread_count(request):
    return JsonResponse({"count":Notification.objects.filter(recipient=request.user,is_read=False).count()})
@login_required
@require_POST
def mark_read(request,pk):
    Notification.objects.filter(pk=pk,recipient=request.user).update(is_read=True)
    return JsonResponse({"ok":True})
@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user,is_read=False).update(is_read=True)
    return JsonResponse({"ok":True})
