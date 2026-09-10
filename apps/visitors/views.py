from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView)

from .models import VisitorAppointment, VisitorLog, WhatsAppConfig
from .forms import AppointmentForm, ArrivalForm, StatusUpdateForm, WhatsAppConfigForm


# ── Access helpers ────────────────────────────────────────────────────────────

def _is_gatekeeper(user):
    return getattr(user, 'is_gatekeeper', False) or user.is_staff

def _can_view_appt(user, appt):
    if user.is_staff or _is_gatekeeper(user) or user.is_head_approver: return True
    if appt.host_user == user: return True
    if user.is_hod and user.department and appt.host_department == user.department: return True
    if appt.booked_by == user: return True
    return False


class GateOrStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return _is_gatekeeper(self.request.user) or self.request.user.is_authenticated


# ── Dashboard ─────────────────────────────────────────────────────────────────

class VisitorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'visitors/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        if user.is_staff or _is_gatekeeper(user) or user.is_head_approver:
            base = VisitorAppointment.objects.all()
        else:
            base = VisitorAppointment.objects.filter(
                Q(host_user=user) |
                Q(host_department=user.department) |
                Q(booked_by=user)
            ).distinct()

        ctx['today']      = today
        ctx['total']      = base.count()
        ctx['scheduled']  = base.filter(status='SCHEDULED').count()
        ctx['arrived']    = base.filter(status='ARRIVED').count()
        ctx['completed']  = base.filter(status='COMPLETED').count()

        ctx['today_appts'] = base.filter(
            scheduled_date=today
        ).exclude(status__in=['CANCELLED','COMPLETED','NO_SHOW']
        ).select_related('host_user','host_department','booked_by').order_by('scheduled_start')

        ctx['upcoming'] = base.filter(
            scheduled_date__gt=today, status='SCHEDULED'
        ).select_related('host_user','host_department').order_by('scheduled_date','scheduled_start')[:10]

        ctx['recent_completed'] = base.filter(
            status__in=['COMPLETED','NO_SHOW']
        ).order_by('-updated_at')[:8]

        ctx['can_create'] = True
        ctx['is_gatekeeper'] = _is_gatekeeper(user)
        return ctx


# ── List ──────────────────────────────────────────────────────────────────────

class AppointmentListView(LoginRequiredMixin, ListView):
    model = VisitorAppointment
    template_name = 'visitors/list.html'
    context_object_name = 'appointments'
    paginate_by = 25

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or _is_gatekeeper(user) or user.is_head_approver:
            qs = VisitorAppointment.objects.all()
        else:
            qs = VisitorAppointment.objects.filter(
                Q(host_user=user)|Q(host_department=user.department)|Q(booked_by=user)
            ).distinct()

        qs = qs.select_related('host_user','host_department','booked_by')
        q      = self.request.GET.get('q','')
        status = self.request.GET.get('status','')
        date_f = self.request.GET.get('date','')

        if q:
            qs = qs.filter(
                Q(visitor_name__icontains=q)|Q(ref_number__icontains=q)|
                Q(visitor_company__icontains=q)|Q(visitor_phone__icontains=q))
        if status: qs = qs.filter(status=status)
        if date_f:
            try:
                from datetime import date
                qs = qs.filter(scheduled_date=date.fromisoformat(date_f))
            except ValueError: pass
        return qs.order_by('-scheduled_date','-scheduled_start')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'q':self.request.GET.get('q',''),
                    'status_f':self.request.GET.get('status',''),
                    'date_f':self.request.GET.get('date',''),
                    'status_choices':VisitorAppointment.Status.choices,
                    'is_gatekeeper':_is_gatekeeper(self.request.user)})
        return ctx


# ── Detail ────────────────────────────────────────────────────────────────────

class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = VisitorAppointment
    template_name = 'visitors/detail.html'
    context_object_name = 'appt'

    def get_object(self):
        a = get_object_or_404(VisitorAppointment, pk=self.kwargs['pk'])
        if not _can_view_appt(self.request.user, a): raise PermissionDenied
        return a

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['logs']           = self.object.logs.select_related('actor')
        ctx['arrival_form']   = ArrivalForm()
        ctx['status_form']    = StatusUpdateForm(initial={'status': self.object.status})
        ctx['is_gatekeeper']  = _is_gatekeeper(self.request.user)
        ctx['info_rows'] = [
            ('Ref Number', a.ref_number),
            ('Status', a.get_status_display()),
            ('Scheduled', f"{a.scheduled_date} {a.scheduled_start}"),
            ('Host', a.host_display),
            ('WhatsApp Sent', 'Yes' if a.arrival_whatsapp_sent else 'No'),
            ('ID Number', a.visitor_id_number or '—'),
            ('Created', a.created_at.strftime('%d %b %Y %H:%M')),
        ]
        ctx['can_update']     = (
            _is_gatekeeper(self.request.user) or self.request.user.is_staff or
            self.object.host_user == self.request.user or self.object.booked_by == self.request.user
        )
        return ctx


# ── Create ────────────────────────────────────────────────────────────────────

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = VisitorAppointment
    form_class = AppointmentForm
    template_name = 'visitors/form.html'

    def form_valid(self, form):
        appt = form.save(commit=False)
        appt.booked_by = self.request.user
        if appt.status == '': appt.status = 'SCHEDULED'
        appt.save()
        VisitorLog.objects.create(
            appointment=appt, actor=self.request.user,
            from_status='', to_status='SCHEDULED', notes='Appointment created.')
        from .notifications import notify_appointment_booked
        notify_appointment_booked(appt)
        messages.success(self.request, f'Appointment {appt.ref_number} booked.')
        return redirect(reverse('visitors:detail', kwargs={'pk': appt.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Book Appointment'
        return ctx


# ── Update ────────────────────────────────────────────────────────────────────

class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = VisitorAppointment
    form_class = AppointmentForm
    template_name = 'visitors/form.html'

    def get_object(self):
        a = get_object_or_404(VisitorAppointment, pk=self.kwargs['pk'])
        if not (self.request.user.is_staff or _is_gatekeeper(self.request.user)
                or a.booked_by == self.request.user or a.host_user == self.request.user):
            raise PermissionDenied
        return a

    def form_valid(self, form):
        appt = form.save()
        messages.success(self.request, f'Appointment {appt.ref_number} updated.')
        return redirect(reverse('visitors:detail', kwargs={'pk': appt.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Edit {self.object.ref_number}'
        return ctx


# ── Status actions ────────────────────────────────────────────────────────────

@login_required
def mark_arrived(request, pk):
    """Gatekeeper checks in a visitor — triggers host notification."""
    appt = get_object_or_404(VisitorAppointment, pk=pk)
    if not (_is_gatekeeper(request.user) or request.user.is_staff):
        raise PermissionDenied
    if request.method == 'POST':
        form = ArrivalForm(request.POST)
        if form.is_valid():
            prev = appt.status
            appt.status      = 'ARRIVED'
            appt.arrived_at  = timezone.now()
            appt.badge_number = form.cleaned_data.get('badge_number', '')
            appt.save(update_fields=['status','arrived_at','badge_number'])
            VisitorLog.objects.create(
                appointment=appt, actor=request.user,
                from_status=prev, to_status='ARRIVED',
                notes=form.cleaned_data.get('notes',''))
            from .notifications import notify_host_on_arrival
            notify_host_on_arrival(appt)
            messages.success(request,
                f'{appt.visitor_name} checked in. Host has been notified.')
    return redirect(reverse('visitors:detail', kwargs={'pk': pk}))


@login_required
def update_status(request, pk):
    """Update appointment status (gatekeeper, host, staff)."""
    appt = get_object_or_404(VisitorAppointment, pk=pk)
    if not (_is_gatekeeper(request.user) or request.user.is_staff
            or appt.host_user == request.user or appt.booked_by == request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            prev   = appt.status
            new_s  = form.cleaned_data['status']
            appt.status = new_s
            if new_s in ('COMPLETED','NO_SHOW'):
                appt.checked_out_at = timezone.now()
            appt.save()
            VisitorLog.objects.create(
                appointment=appt, actor=request.user,
                from_status=prev, to_status=new_s,
                notes=form.cleaned_data.get('notes',''))
            if new_s == 'CANCELLED':
                from .notifications import notify_appointment_cancelled
                notify_appointment_cancelled(appt)
            messages.success(request, f'Status updated to {appt.get_status_display()}.')
    return redirect(reverse('visitors:detail', kwargs={'pk': pk}))


# ── WhatsApp config (staff only) ──────────────────────────────────────────────

class WhatsAppConfigView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'visitors/whatsapp_config.html'

    def test_func(self): return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cfg = WhatsAppConfig.objects.filter(is_active=True).first()
        ctx['form'] = WhatsAppConfigForm(instance=cfg)
        ctx['cfg']  = cfg
        return ctx

    def post(self, request, *args, **kwargs):
        cfg = WhatsAppConfig.objects.filter(is_active=True).first()
        form = WhatsAppConfigForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save()
            messages.success(request, 'WhatsApp configuration saved.')
            return redirect(reverse('visitors:whatsapp_config'))
        return self.render_to_response(self.get_context_data(form=form))


@login_required
def test_whatsapp(request):
    """Send a test WhatsApp message."""
    if not request.user.is_staff: raise PermissionDenied
    if request.method == 'POST':
        to   = request.POST.get('test_to','').strip()
        msg  = request.POST.get('test_msg','Test message from ProcureDesk.').strip()
        if not to:
            messages.error(request, 'Enter a phone number.')
        else:
            from .whatsapp import send_whatsapp
            ok = send_whatsapp(to, msg)
            if ok:
                messages.success(request, f'Test message sent to {to}.')
            else:
                messages.error(request, 'Failed to send — check configuration and logs.')
    return redirect(reverse('visitors:whatsapp_config'))


def api_docs(request):
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import render
    endpoints = [
        {"method":"GET","path":"/visitors/api/appointments/","title":"List appointments",
         "description":"Returns paginated appointments scoped to the calling user's role. Supports ?status=, ?date=YYYY-MM-DD, ?q=, ?page=, ?per_page=.",
         "params":"","example":'{"total":5,"page":1,"per_page":20,"results":[...]}'},
        {"method":"POST","path":"/visitors/api/appointments/","title":"Create appointment",
         "description":"Book a new visitor appointment.",
         "params":"visitor_name* (str), scheduled_date* (YYYY-MM-DD), scheduled_start* (HH:MM), host_user (id) OR host_department (id), visitor_phone, visitor_company, agenda, vehicle_plate, vehicle_make, vehicle_colour",
         "example":'{"appointment":{"ref_number":"VIS-20250101-A1B2C","status":"SCHEDULED",...}}'},
        {"method":"GET","path":"/visitors/api/appointments/<ref>/","title":"Appointment detail",
         "description":"Full detail of a single appointment by ref_number.",
         "params":"","example":'{"appointment":{...}}'},
        {"method":"POST","path":"/visitors/api/appointments/<ref>/arrive/","title":"Check in visitor",
         "description":"Gatekeeper marks visitor as arrived. Triggers host notification and WhatsApp.",
         "params":"badge_number (str, optional), notes (str, optional)",
         "example":'{"appointment":{...},"message":"Visitor checked in."}'},
        {"method":"POST","path":"/visitors/api/appointments/<ref>/status/","title":"Update status",
         "description":"Change appointment status. Valid values: ARRIVED, IN_MEETING, COMPLETED, NO_SHOW, CANCELLED.",
         "params":"status* (str), notes (str, optional)",
         "example":'{"appointment":{...}}'},
        {"method":"GET","path":"/visitors/api/today/","title":"Today's appointments",
         "description":"Convenience endpoint — returns all non-cancelled appointments for today.",
         "params":"","example":'{"date":"2025-01-15","count":3,"appointments":[...]}'},
        {"method":"GET","path":"/visitors/api/users/","title":"User list",
         "description":"All active users — for populating host selection in the mobile app.",
         "params":"","example":'{"users":[{"id":1,"name":"Jane Doe","email":"jane@example.com","department":{...}},...]}'},
        {"method":"GET","path":"/visitors/api/departments/","title":"Department list",
         "description":"All departments — for host department selection.",
         "params":"","example":'{"departments":[{"id":1,"name":"Finance","code":"FIN"},...]}'},
    ]
    return render(request, "visitors/api_docs.html", {"endpoints": endpoints})
