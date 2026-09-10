from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse
from django.db.models import Q

from .models import PurchaseOrder, POLineItem
from .forms import PurchaseOrderForm, POLineItemFormSet, ApprovalForm, RejectionForm, ItemRejectionForm
from .utils import POWorkflow, WorkflowError

# Status steps for the stepper UI
PO_STEPS = [
    ('DRAFT',        'Draft',       1),
    ('PENDING_HOD',  'HOD Review',  2),
    ('PENDING_HEAD', 'Head Review', 3),
    ('SENT_PROC',    'Procurement', 4),
    ('ORDERED',      'Ordered',     5),
    ('RECEIVED',     'Received',    6),
]

# Which steps count as "done" once past them
STEP_ORDER = ['DRAFT','PENDING_HOD','PENDING_HEAD','APPROVED','SENT_PROC','ORDERED','RECEIVED']

def _steps_context(po):
    status = po.status
    if status in ('REJECTED', 'CANCELLED'):
        try:
            log = po.logs.exclude(to_status__in=['REJECTED','CANCELLED']).last()
            rejected_at = log.to_status if log else 'DRAFT'
        except Exception:
            rejected_at = 'DRAFT'
    else:
        rejected_at = None

    try:
        current_idx = STEP_ORDER.index(status)
    except ValueError:
        current_idx = 0

    done_statuses = STEP_ORDER[:current_idx]
    return {
        'steps': PO_STEPS,
        'step_done': done_statuses,
        'rejected_at_step': rejected_at,
    }


class POListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchase_orders/list.html'
    context_object_name = 'pos'
    paginate_by = 25

    def get_queryset(self):
        user = self.request.user
        qs = PurchaseOrder.objects.select_related(
            'requester', 'department', 'hod_approver', 'head_approver')
        if user.is_head_approver or user.is_staff or user.is_procurement_officer:
            pass
        elif user.is_hod:
            qs = qs.filter(Q(requester=user) | Q(department=user.department))
        else:
            qs = qs.filter(requester=user)

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(po_number__icontains=q) | Q(title__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = PurchaseOrder.Status.choices
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['q'] = self.request.GET.get('q', '')
        user = self.request.user
        if user.is_head_approver:
            ctx['pending_count'] = PurchaseOrder.objects.filter(
                status=PurchaseOrder.Status.PENDING_HEAD).count()
        elif user.is_hod:
            ctx['pending_count'] = PurchaseOrder.objects.filter(
                status=PurchaseOrder.Status.PENDING_HOD,
                department=user.department).count()
        return ctx


class PODetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchase_orders/detail.html'
    context_object_name = 'po'

    def get_object(self):
        po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        user = self.request.user
        if (user.is_head_approver or user.is_staff or user.is_procurement_officer
                or user.is_storekeeper or po.requester == user
                or (user.is_hod and user.department == po.department)):
            return po
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        po = self.object
        user = self.request.user
        ctx.update(_steps_context(po))
        ctx['can_submit']       = po.can_be_submitted_by(user)
        ctx['can_hod_approve']  = po.can_be_hod_approved_by(user)
        ctx['can_head_approve'] = po.can_be_head_approved_by(user)
        ctx['can_reject']       = po.can_be_rejected_by(user)
        ctx['can_reject_items'] = po.can_reject_items_as(user)
        ctx['can_cancel']       = po.can_be_cancelled_by(user)
        ctx['can_edit']         = po.is_editable_by(user)
        ctx['linked_tickets'] = po.tickets.select_related('created_by', 'assigned_to').order_by('-created_at') if hasattr(po, 'tickets') else []
        ctx['approval_trail'] = [
            ('HOD Approval',  po.hod_approver,  po.hod_approved_at,  bool(po.hod_approver)),
            ('Head Approval', po.head_approver, po.head_approved_at, bool(po.head_approver)),
            ('Procurement',   po.procurement_officer, po.sent_to_procurement_at,
             po.status in ('SENT_PROC','ORDERED','RECEIVED')),
        ]
        return ctx


class POCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchase_orders/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['formset'] = (POLineItemFormSet(self.request.POST, self.request.FILES)
                          if self.request.POST else POLineItemFormSet())
        ctx['page_title'] = 'New Purchase Order'
        return ctx

    def form_valid(self, form):
        formset = POLineItemFormSet(self.request.POST, self.request.FILES)
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        user = self.request.user
        po = form.save(commit=False)
        po.requester = user
        po.department = user.department
        po.save()
        formset.instance = po
        instances = formset.save(commit=False)
        for i, obj in enumerate(instances):
            obj.sort_order = i
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        messages.success(self.request, f'PO {po.po_number} created.')
        return redirect(reverse('purchase_orders:detail', kwargs={'pk': po.pk}))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class POUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchase_orders/form.html'

    def get_object(self):
        po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        if not po.is_editable_by(self.request.user):
            raise PermissionDenied
        return po

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['formset'] = (
            POLineItemFormSet(self.request.POST, self.request.FILES, instance=self.object)
            if self.request.POST else POLineItemFormSet(instance=self.object))
        ctx['page_title'] = f'Edit {self.object.po_number}'
        return ctx

    def form_valid(self, form):
        formset = POLineItemFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        po = form.save()
        instances = formset.save(commit=False)
        for i, obj in enumerate(instances):
            obj.sort_order = i
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        po.recalculate_total()
        messages.success(self.request, 'PO updated.')
        return redirect(reverse('purchase_orders:detail', kwargs={'pk': po.pk}))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


@login_required
def submit_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        try:
            POWorkflow.submit(po, request.user)
            messages.success(request, f'{po.po_number} submitted.')
        except WorkflowError as e:
            messages.error(request, str(e))
    return redirect(reverse('purchase_orders:detail', kwargs={'pk': pk}))


@login_required
def hod_approve_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        try:
            POWorkflow.hod_approve(po, request.user, comment=request.POST.get('comment', ''))
            messages.success(request, f'{po.po_number} approved and forwarded to head approver.')
        except WorkflowError as e:
            messages.error(request, str(e))
    return redirect(reverse('purchase_orders:detail', kwargs={'pk': pk}))


@login_required
def head_approve_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        try:
            POWorkflow.head_approve(po, request.user, comment=request.POST.get('comment', ''))
            messages.success(request, f'{po.po_number} approved and sent to procurement.')
        except WorkflowError as e:
            messages.error(request, str(e))
    return redirect(reverse('purchase_orders:detail', kwargs={'pk': pk}))


@login_required
def reject_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        try:
            POWorkflow.reject(po, request.user, reason=reason)
            messages.warning(request, f'{po.po_number} has been rejected.')
        except WorkflowError as e:
            messages.error(request, str(e))
    return redirect(reverse('purchase_orders:detail', kwargs={'pk': pk}))


@login_required
def reject_items(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        reason   = request.POST.get('reason', '').strip()
        try:
            POWorkflow.reject_items(po, request.user, item_ids=item_ids, reason=reason)
            messages.warning(request, 'Selected item(s) have been rejected.')
        except WorkflowError as e:
            messages.error(request, str(e))
    return redirect(reverse('purchase_orders:detail', kwargs={'pk': pk}))


@login_required
def cancel_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        try:
            POWorkflow.cancel(po, request.user)
            messages.info(request, f'{po.po_number} cancelled.')
        except WorkflowError as e:
            messages.error(request, str(e))
    return redirect(reverse('purchase_orders:list'))


@login_required
def save_signature(request, pk):
    """AJAX POST — saves base64 signature for the caller's role on the PO."""
    from django.utils import timezone as tz
    import json
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST
    sig = (data.get('signature') or '').strip()
    if not sig:
        from django.http import JsonResponse
        return JsonResponse({'error': 'No signature data'}, status=400)
    user = request.user
    now = tz.now()
    if po.requester == user:
        po.signature_requester = sig; po.signature_requester_at = now
        po.save(update_fields=['signature_requester','signature_requester_at'])
    elif user.is_hod and user.department == po.department:
        po.signature_hod = sig; po.signature_hod_at = now
        po.save(update_fields=['signature_hod','signature_hod_at'])
    elif user.is_head_approver:
        po.signature_head = sig; po.signature_head_at = now
        po.save(update_fields=['signature_head','signature_head_at'])
    else:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Not authorised'}, status=403)
    from django.http import JsonResponse
    return JsonResponse({'ok': True})


@login_required
def export_po_pdf(request, pk):
    """Download PO as PDF with signatures."""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    u = request.user
    if not (u.is_head_approver or u.is_staff or u.is_procurement_officer
            or po.requester == u
            or (u.is_hod and u.department == po.department)):
        raise PermissionDenied
    try:
        from .pdf_export import generate_po_pdf
        from django.http import HttpResponse
        buf = generate_po_pdf(po)
        resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{po.po_number}.pdf"'
        return resp
    except ImportError:
        messages.error(request, 'PDF export requires ReportLab. Run: pip install reportlab')
        return redirect(reverse('purchase_orders:detail', kwargs={'pk': pk}))
