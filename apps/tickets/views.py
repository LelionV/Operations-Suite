import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView

from .models import Ticket, TicketComment, TicketAttachment
from .forms import TicketForm, TicketStatusForm, TicketCommentForm


# ── Access control helpers ──────────────────────────────────────────────────

def _require_ticket_access(user):
    """Raises PermissionDenied if the user has no ticket access."""
    if not user.has_ticket_access():
        raise PermissionDenied


def _can_view(user, ticket):
    """
    ticket_viewer  → sees ALL tickets
    staff / head_approver → sees ALL tickets
    HOD            → sees own dept tickets
    can_access_tickets user → sees own dept tickets + their own raised tickets
    """
    if not user.has_ticket_access():
        return False
    if user.is_ticket_viewer or user.is_staff or user.is_head_approver:
        return True
    if ticket.created_by == user:
        return True
    if user.department and ticket.department == user.department:
        return True
    return False


def _can_manage(user, ticket):
    """
    Can update status / add comments.
    ticket_viewer can VIEW but NOT manage.
    """
    if user.is_ticket_viewer:
        return False
    if user.is_staff or user.is_head_approver:
        return True
    if user.is_hod and user.department == ticket.department:
        return True
    if user.can_access_tickets and ticket.created_by == user:
        return True
    return False


def _base_queryset(user):
    """Return ticket queryset scoped to what the user is allowed to see."""
    qs = Ticket.objects.select_related('created_by', 'department', 'purchase_order')
    if user.is_ticket_viewer or user.is_staff or user.is_head_approver:
        return qs  # see everything
    return qs.filter(
        Q(created_by=user) | Q(department=user.department)
    ).distinct()


# ── Mixin ───────────────────────────────────────────────────────────────────

class TicketAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.has_ticket_access():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# ── Dashboard ───────────────────────────────────────────────────────────────

class TicketDashboardView(TicketAccessMixin, TemplateView):
    template_name = 'tickets/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        base_qs = _base_queryset(user)

        ctx['total']       = base_qs.count()
        ctx['open']        = base_qs.filter(status='open').count()
        ctx['in_progress'] = base_qs.filter(status='in_progress').count()
        ctx['resolved']    = base_qs.filter(status='resolved').count()
        ctx['closed']      = base_qs.filter(status='closed').count()

        from django.utils import timezone
        active = base_qs.exclude(status__in=['resolved', 'closed'])
        overdue = [t for t in active.exclude(expected_resolution_date__isnull=True)
                   if t.is_overdue()]
        ctx['overdue_count']   = len(overdue)
        ctx['overdue_tickets'] = overdue[:10]
        ctx['recent']          = base_qs.order_by('-created_at')[:8]

        # ── Per-department summary (chart data) ──────────────────────────
        from apps.departments.models import Department
        departments = Department.objects.all()
        dept_summary = []
        for dept in departments:
            dept_qs = Ticket.objects.filter(department=dept)
            open_c  = dept_qs.filter(status='open').count()
            prog_c  = dept_qs.filter(status='in_progress').count()
            res_c   = dept_qs.filter(status='resolved').count()
            clo_c   = dept_qs.filter(status='closed').count()
            total   = open_c + prog_c + res_c + clo_c
            if total == 0 and not (user.is_ticket_viewer or user.is_staff or user.is_head_approver):
                continue
            dept_summary.append({
                'name':        dept.name,
                'open':        open_c,
                'in_progress': prog_c,
                'resolved':    res_c,
                'closed':      clo_c,
                'total':       total,
            })
        ctx['dept_summary'] = json.dumps(dept_summary)
        ctx['dept_summary_list'] = dept_summary
        return ctx


# ── List ────────────────────────────────────────────────────────────────────

class TicketListView(TicketAccessMixin, ListView):
    model = Ticket
    template_name = 'tickets/list.html'
    context_object_name = 'tickets'
    paginate_by = 25

    def get_queryset(self):
        qs = _base_queryset(self.request.user)
        q        = self.request.GET.get('q', '')
        status   = self.request.GET.get('status', '')
        priority = self.request.GET.get('priority', '')
        dept     = self.request.GET.get('dept', '')
        if q:
            qs = qs.filter(Q(code__icontains=q) | Q(title__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if dept:
            qs = qs.filter(department_id=dept)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'q':        self.request.GET.get('q', ''),
            'status_f': self.request.GET.get('status', ''),
            'prio_f':   self.request.GET.get('priority', ''),
            'dept_f':   self.request.GET.get('dept', ''),
            'status_choices':   Ticket.STATUS_CHOICES,
            'priority_choices': Ticket.PRIORITY_CHOICES,
        })
        from apps.departments.models import Department
        ctx['departments'] = Department.objects.all()
        user = self.request.user
        base = _base_queryset(user)
        ctx['open_count'] = base.filter(status='open').count()
        return ctx


# ── Detail ───────────────────────────────────────────────────────────────────

class TicketDetailView(TicketAccessMixin, DetailView):
    model = Ticket
    template_name = 'tickets/detail.html'
    context_object_name = 'ticket'

    def get_object(self):
        t = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        if not _can_view(self.request.user, t):
            raise PermissionDenied
        return t

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        t    = self.object
        user = self.request.user
        ctx['comment_form'] = TicketCommentForm()
        ctx['status_form']  = TicketStatusForm(instance=t)
        ctx['can_manage']   = _can_manage(user, t)
        ctx['can_close']    = (
            t.status == 'resolved' and t.created_by == user
        ) or user.is_staff
        ctx['ticket_meta'] = [
            ('Code',           t.code),
            ('Department',     str(t.department) if t.department else '—'),
            ('Priority',       t.get_priority_display()),
            ('Status',         t.get_status_display()),
            ('Created By',     t.created_by.get_full_name() or t.created_by.username),
            ('Created',        t.created_at.strftime('%d %b %Y %H:%M')),
            ('Updated',        t.updated_at.strftime('%d %b %Y %H:%M')),
            ('Expected',       t.expected_resolution_date.strftime('%d %b %Y %H:%M') if t.expected_resolution_date else '—'),
            ('Resolved',       t.resolved_at.strftime('%d %b %Y %H:%M') if t.resolved_at else '—'),
            ('Linked PO',      t.purchase_order.po_number if t.purchase_order else '—'),
        ]
        return ctx


# ── Create ───────────────────────────────────────────────────────────────────

class TicketCreateView(TicketAccessMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/form.html'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['user'] = self.request.user
        return kw

    def get_initial(self):
        init = super().get_initial()
        po_pk = self.request.GET.get('po')
        if po_pk:
            from apps.purchase_orders.models import PurchaseOrder
            try:
                init['purchase_order'] = PurchaseOrder.objects.get(pk=po_pk)
            except PurchaseOrder.DoesNotExist:
                pass
        return init

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.created_by = self.request.user
        ticket.save()
        from .utils import notify_ticket
        notify_ticket(ticket, event='created')
        messages.success(self.request, f'Ticket {ticket.code} created.')
        return redirect(reverse('tickets:detail', kwargs={'pk': ticket.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'New Ticket'
        return ctx


# ── Update ───────────────────────────────────────────────────────────────────

class TicketUpdateView(TicketAccessMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/form.html'

    def get_object(self):
        t = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        if not _can_manage(self.request.user, t):
            raise PermissionDenied
        return t

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['user'] = self.request.user
        return kw

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.updated_by = self.request.user
        ticket.save()
        messages.success(self.request, f'Ticket {ticket.code} updated.')
        return redirect(reverse('tickets:detail', kwargs={'pk': ticket.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Edit {self.object.code}'
        return ctx


# ── Action views ─────────────────────────────────────────────────────────────

@login_required
def update_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    _require_ticket_access(request.user)
    if not _can_manage(request.user, ticket):
        raise PermissionDenied
    if request.method == 'POST':
        form = TicketStatusForm(request.POST, instance=ticket)
        if form.is_valid():
            prev_status = ticket.status
            t = form.save(commit=False)
            t.updated_by = request.user
            t.save()
            # Only notify on meaningful status changes
            if t.status != prev_status:
                from .utils import notify_ticket
                notify_ticket(t, event=t.status)
            messages.success(request,
                f'Ticket {ticket.code} moved to {t.get_status_display()}.')
    return redirect(reverse('tickets:detail', kwargs={'pk': pk}))


@login_required
def add_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    _require_ticket_access(request.user)
    if not _can_view(request.user, ticket):
        raise PermissionDenied
    if request.method == 'POST':
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.ticket = ticket
            c.sender = request.user
            c.save()
            for f in request.FILES.getlist('attachments'):
                TicketAttachment.objects.create(
                    ticket=ticket, file=f, uploaded_by=request.user)
            # No email on comments — only on status change
            messages.success(request, 'Comment added.')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect(reverse('tickets:detail', kwargs={'pk': pk}))


@login_required
def download_attachment(request, ticket_id, file_id):
    att = get_object_or_404(TicketAttachment, id=file_id, ticket_id=ticket_id)
    _require_ticket_access(request.user)
    if not _can_view(request.user, att.ticket):
        raise PermissionDenied
    if not att.file:
        raise Http404
    return FileResponse(att.file.open('rb'), as_attachment=True, filename=att.filename())


@login_required
def close_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    _require_ticket_access(request.user)
    can_close = (
        (ticket.status == 'resolved' and ticket.created_by == request.user)
        or request.user.is_staff
    )
    if not can_close:
        raise PermissionDenied
    if request.method == 'POST':
        ticket.close()
        from .utils import notify_ticket
        notify_ticket(ticket, event='closed')
        messages.success(request, f'Ticket {ticket.code} closed.')
    return redirect(reverse('tickets:detail', kwargs={'pk': pk}))
