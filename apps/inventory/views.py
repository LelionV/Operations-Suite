from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy

from .forms import QBUploadForm
from .models import QBItem, QBUploadLog
from .services import import_qb_items, UploadError


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_head_approver


class QBUploadView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    template_name = 'inventory/upload.html'
    form_class = QBUploadForm
    success_url = reverse_lazy('inventory:item_list')

    def form_valid(self, form):
        f = self.request.FILES['file']
        try:
            log = import_qb_items(f, f.name, self.request.user)
            messages.success(
                self.request,
                f'Import complete: {log.rows_created} created, '
                f'{log.rows_updated} updated, {log.rows_skipped} skipped.',
            )
        except UploadError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)


class QBItemListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = QBItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 50

    def get_queryset(self):
        qs = QBItem.objects.filter(is_active=True)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(code__icontains=q) | qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['logs'] = QBUploadLog.objects.all()[:5]
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


def qb_item_search(request):
    """
    AJAX endpoint — used by the PO line item form to search QB items.
    Returns JSON: [{code, name, uom}, ...]
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse([], safe=False)
    items = QBItem.objects.filter(is_active=True).filter(
        code__icontains=q
    ) | QBItem.objects.filter(is_active=True).filter(name__icontains=q)
    data = list(items.values('code', 'name', 'uom')[:30])
    return JsonResponse(data, safe=False)
