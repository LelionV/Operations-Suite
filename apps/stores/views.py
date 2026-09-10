from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.purchase_orders.models import PurchaseOrder, ApprovalLog
from .models import GoodsReceivedNote, GRNLineItem
from .forms import GRNForm


class StorekeeperRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_storekeeper or self.request.user.is_staff


class StoresDashboardView(StorekeeperRequiredMixin, ListView):
    template_name = 'stores/dashboard.html'
    context_object_name = 'pending'

    def get_queryset(self):
        return PurchaseOrder.objects.filter(
            status=PurchaseOrder.Status.ORDERED
        ).select_related('department', 'requester').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['partial'] = GoodsReceivedNote.objects.filter(
            status=GoodsReceivedNote.GRNStatus.PARTIAL
        ).select_related('purchase_order')
        ctx['completed'] = GoodsReceivedNote.objects.filter(
            status=GoodsReceivedNote.GRNStatus.COMPLETE
        ).select_related('purchase_order').order_by('-received_at')[:15]
        return ctx


class GRNCreateView(StorekeeperRequiredMixin, CreateView):
    model = GoodsReceivedNote
    form_class = GRNForm
    template_name = 'stores/grn_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.po = get_object_or_404(
            PurchaseOrder, pk=self.kwargs['po_pk'],
            status=PurchaseOrder.Status.ORDERED)
        if hasattr(self.po, 'grn'):
            messages.info(request, 'GRN already exists for this PO.')
            return redirect(reverse('stores:grn_detail', kwargs={'pk': self.po.grn.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['po'] = self.po
        ctx['active_items'] = list(self.po.active_line_items)
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        po = self.po
        grn = form.save(commit=False)
        grn.purchase_order = po
        grn.received_by = self.request.user
        grn.save()

        for item in po.active_line_items:
            try:
                qty = int(self.request.POST.get(f'qty_{item.pk}', 0) or 0)
            except (ValueError, TypeError):
                qty = 0
            GRNLineItem.objects.create(
                grn=grn, po_line_item=item,
                qty_received=qty,
                condition=self.request.POST.get(f'cond_{item.pk}', ''),
                notes=self.request.POST.get(f'note_{item.pk}', ''),
            )

        grn.refresh_status()

        prev = po.status
        po.status = PurchaseOrder.Status.RECEIVED
        po.save()
        ApprovalLog.objects.create(
            purchase_order=po, actor=self.request.user,
            from_status=prev, to_status=po.status,
            comment=f'GRN {grn.grn_number} created — {grn.get_status_display()}.',
        )
        from apps.notifications.utils import notify_grn_created
        notify_grn_created(po, grn)
        messages.success(self.request, f'GRN {grn.grn_number} saved.')
        return redirect(reverse('stores:grn_detail', kwargs={'pk': grn.pk}))


class GRNDetailView(LoginRequiredMixin, DetailView):
    """
    Visible to: storekeepers, staff, the requester, and all members
    of the PO's department.
    """
    model = GoodsReceivedNote
    template_name = 'stores/grn_detail.html'
    context_object_name = 'grn'

    def get_object(self):
        grn = get_object_or_404(GoodsReceivedNote, pk=self.kwargs['pk'])
        user = self.request.user
        po = grn.purchase_order
        if (user.is_storekeeper or user.is_staff or user.is_head_approver
                or user.is_procurement_officer
                or po.requester == user
                or (user.department and user.department == po.department)):
            return grn
        raise PermissionDenied


class GRNUpdateView(StorekeeperRequiredMixin, UpdateView):
    model = GoodsReceivedNote
    form_class = GRNForm
    template_name = 'stores/grn_form.html'

    def dispatch(self, request, *args, **kwargs):
        grn = get_object_or_404(GoodsReceivedNote, pk=self.kwargs['pk'])
        if grn.status == GoodsReceivedNote.GRNStatus.COMPLETE:
            messages.info(request, 'GRN is fully received.')
            return redirect(reverse('stores:grn_detail', kwargs={'pk': grn.pk}))
        self.po = grn.purchase_order
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['po'] = self.po
        ctx['grn'] = self.object
        ctx['active_items'] = list(self.po.active_line_items)
        ctx['grn_map'] = {g.po_line_item_id: g for g in self.object.grn_items.all()}
        ctx['is_edit'] = True
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        grn = form.save()
        grn_map = {g.po_line_item_id: g for g in grn.grn_items.all()}
        for item in self.po.active_line_items:
            try:
                qty = int(self.request.POST.get(f'qty_{item.pk}', 0) or 0)
            except (ValueError, TypeError):
                qty = 0
            gl = grn_map.get(item.pk)
            if gl:
                gl.qty_received = qty
                gl.condition    = self.request.POST.get(f'cond_{item.pk}', gl.condition)
                gl.notes        = self.request.POST.get(f'note_{item.pk}', gl.notes)
                gl.save()
        grn.refresh_status()
        messages.success(self.request, f'GRN {grn.grn_number} updated.')
        return redirect(reverse('stores:grn_detail', kwargs={'pk': grn.pk}))


class ReceivedItemsView(LoginRequiredMixin, ListView):
    """
    Shows all RECEIVED POs to: the requester, dept members,
    storekeepers, procurement, head approver, staff.
    Requesters and dept members only see their own department's GRNs.
    """
    template_name = 'stores/received_list.html'
    context_object_name = 'grns'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = GoodsReceivedNote.objects.select_related(
            'purchase_order', 'purchase_order__department',
            'purchase_order__requester', 'received_by'
        ).order_by('-received_at')

        if user.is_storekeeper or user.is_staff or user.is_head_approver or user.is_procurement_officer:
            pass  # see all
        elif user.department:
            qs = qs.filter(purchase_order__department=user.department)
        else:
            qs = qs.filter(purchase_order__requester=user)

        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                Q(grn_number__icontains=q) |
                Q(purchase_order__po_number__icontains=q) |
                Q(purchase_order__title__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx
