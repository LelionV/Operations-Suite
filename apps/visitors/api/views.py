"""
REST API for the Visitor Management module.
Designed for mobile app integration.
No external DRF required — uses plain Django JsonResponse.

Endpoints:
  GET  /visitors/api/appointments/          — list (filtered by date/status)
  POST /visitors/api/appointments/          — create appointment
  GET  /visitors/api/appointments/<ref>/    — detail by ref_number
  POST /visitors/api/appointments/<ref>/arrive/  — check in visitor
  POST /visitors/api/appointments/<ref>/status/  — update status
  GET  /visitors/api/today/                 — today's appointments
  POST /visitors/api/whatsapp/test/         — test WhatsApp send (staff)
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.utils import timezone
from functools import wraps


def _auth_required(view_func):
    """
    Simple token / basic auth decorator.
    Accepts either:
      - Authorization: Token <user.auth_token>   (if rest_framework is installed)
      - Authorization: Basic <base64 user:pass>
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        user = None

        if auth.startswith('Basic '):
            import base64
            try:
                creds = base64.b64decode(auth[6:]).decode('utf-8')
                username, password = creds.split(':', 1)
                user = authenticate(request, username=username, password=password)
            except Exception:
                pass
        elif auth.startswith('Token '):
            token = auth[6:].strip()
            try:
                # Works with DRF Token if installed
                from rest_framework.authtoken.models import Token
                user = Token.objects.get(key=token).user
            except Exception:
                # Fallback: match against a DB-stored API key field (not implemented here)
                pass

        if not user or not user.is_active:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        request.api_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


def _appt_to_dict(a):
    return {
        'id':            a.pk,
        'ref_number':    a.ref_number,
        'visitor_name':  a.visitor_name,
        'visitor_email': a.visitor_email,
        'visitor_phone': a.visitor_phone,
        'visitor_company': a.visitor_company,
        'visitor_id_number': a.visitor_id_number,
        'host_user':     {'id': a.host_user.pk, 'name': a.host_user.get_full_name()} if a.host_user else None,
        'host_department': {'id': a.host_department.pk, 'name': a.host_department.name} if a.host_department else None,
        'scheduled_date':  str(a.scheduled_date),
        'scheduled_start': str(a.scheduled_start),
        'scheduled_end':   str(a.scheduled_end) if a.scheduled_end else None,
        'agenda':          a.agenda,
        'vehicle_plate':   a.vehicle_plate,
        'vehicle_make':    a.vehicle_make,
        'vehicle_colour':  a.vehicle_colour,
        'status':          a.status,
        'status_display':  a.get_status_display(),
        'badge_number':    a.badge_number,
        'arrived_at':      a.arrived_at.isoformat() if a.arrived_at else None,
        'checked_out_at':  a.checked_out_at.isoformat() if a.checked_out_at else None,
        'booked_by':       a.booked_by.get_full_name() if a.booked_by else None,
        'notes':           a.notes,
        'created_at':      a.created_at.isoformat(),
    }


@csrf_exempt
@_auth_required
@require_http_methods(['GET', 'POST'])
def appointment_list_create(request):
    from ..models import VisitorAppointment
    from django.db.models import Q

    if request.method == 'GET':
        user = request.api_user
        qs = VisitorAppointment.objects.select_related('host_user','host_department','booked_by')

        # Scope by role
        if not (user.is_staff or getattr(user,'is_gatekeeper',False) or user.is_head_approver):
            qs = qs.filter(
                Q(host_user=user)|Q(host_department=user.department)|Q(booked_by=user)
            ).distinct()

        # Filters
        status = request.GET.get('status','')
        date   = request.GET.get('date','')
        q      = request.GET.get('q','')
        if status: qs = qs.filter(status=status)
        if date:
            try:
                from datetime import date as ddate
                qs = qs.filter(scheduled_date=ddate.fromisoformat(date))
            except ValueError: pass
        if q:
            qs = qs.filter(Q(visitor_name__icontains=q)|Q(ref_number__icontains=q)|
                           Q(visitor_company__icontains=q))

        page    = int(request.GET.get('page', 1))
        per     = int(request.GET.get('per_page', 20))
        total   = qs.count()
        results = qs.order_by('-scheduled_date','-scheduled_start')[(page-1)*per:page*per]
        return JsonResponse({
            'total': total, 'page': page, 'per_page': per,
            'results': [_appt_to_dict(a) for a in results]
        })

    # POST — create
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required = ['visitor_name','scheduled_date','scheduled_start']
    for f in required:
        if not data.get(f):
            return JsonResponse({'error': f'{f} is required.'}, status=400)

    if not data.get('host_user') and not data.get('host_department'):
        return JsonResponse({'error': 'Provide host_user (id) or host_department (id).'}, status=400)

    from ..models import VisitorAppointment
    from apps.accounts.models import User

    from apps.departments.models import Department

    appt = VisitorAppointment()
    appt.visitor_name      = data['visitor_name']
    appt.visitor_email     = data.get('visitor_email','')
    appt.visitor_phone     = data.get('visitor_phone','')
    appt.visitor_company   = data.get('visitor_company','')
    appt.visitor_id_number = data.get('visitor_id_number','')
    appt.scheduled_date    = data['scheduled_date']
    appt.scheduled_start   = data['scheduled_start']
    appt.scheduled_end     = data.get('scheduled_end')
    appt.agenda            = data.get('agenda','')
    appt.vehicle_plate     = data.get('vehicle_plate','')
    appt.vehicle_make      = data.get('vehicle_make','')
    appt.vehicle_colour    = data.get('vehicle_colour','')
    appt.notes             = data.get('notes','')
    appt.status            = 'SCHEDULED'
    appt.booked_by         = request.api_user

    if data.get('host_user'):
        try: appt.host_user = User.objects.get(pk=data['host_user'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'host_user not found.'}, status=404)

    if data.get('host_department'):
        try: appt.host_department = Department.objects.get(pk=data['host_department'])
        except Department.DoesNotExist:
            return JsonResponse({'error': 'host_department not found.'}, status=404)

    appt.save()
    from ..models import VisitorLog
    VisitorLog.objects.create(appointment=appt, actor=request.api_user,
        from_status='', to_status='SCHEDULED', notes='Created via API.')
    from ..notifications import notify_appointment_booked
    notify_appointment_booked(appt)

    return JsonResponse({'appointment': _appt_to_dict(appt)}, status=201)


@csrf_exempt
@_auth_required
@require_http_methods(['GET'])
def appointment_detail(request, ref):
    from ..models import VisitorAppointment
    try:
        appt = VisitorAppointment.objects.select_related(
            'host_user','host_department','booked_by').get(ref_number=ref)
    except VisitorAppointment.DoesNotExist:
        return JsonResponse({'error': 'Not found.'}, status=404)
    user = request.api_user
    from ..views import _can_view_appt
    if not _can_view_appt(user, appt):
        return JsonResponse({'error': 'Forbidden.'}, status=403)
    return JsonResponse({'appointment': _appt_to_dict(appt)})


@csrf_exempt
@_auth_required
@require_http_methods(['POST'])
def appointment_arrive(request, ref):
    """Mark visitor as arrived — gatekeeper action."""
    from ..models import VisitorAppointment, VisitorLog
    user = request.api_user
    if not (getattr(user,'is_gatekeeper',False) or user.is_staff):
        return JsonResponse({'error': 'Gatekeeper or staff required.'}, status=403)

    try:
        appt = VisitorAppointment.objects.get(ref_number=ref)
    except VisitorAppointment.DoesNotExist:
        return JsonResponse({'error': 'Not found.'}, status=404)

    try: data = json.loads(request.body)
    except Exception: data = {}

    prev = appt.status
    appt.status       = 'ARRIVED'
    appt.arrived_at   = timezone.now()
    appt.badge_number = data.get('badge_number','')
    appt.save(update_fields=['status','arrived_at','badge_number'])
    VisitorLog.objects.create(appointment=appt, actor=user,
        from_status=prev, to_status='ARRIVED', notes=data.get('notes','API check-in.'))
    from ..notifications import notify_host_on_arrival
    notify_host_on_arrival(appt)

    return JsonResponse({'appointment': _appt_to_dict(appt), 'message': 'Visitor checked in.'})


@csrf_exempt
@_auth_required
@require_http_methods(['POST'])
def appointment_status(request, ref):
    """Update appointment status."""
    from ..models import VisitorAppointment, VisitorLog
    user = request.api_user

    try:
        appt = VisitorAppointment.objects.get(ref_number=ref)
    except VisitorAppointment.DoesNotExist:
        return JsonResponse({'error': 'Not found.'}, status=404)

    from ..views import _can_view_appt
    if not _can_view_appt(user, appt):
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    try: data = json.loads(request.body)
    except Exception: return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    valid = [s for s,_ in VisitorAppointment.Status.choices]
    new_s = data.get('status','')
    if new_s not in valid:
        return JsonResponse({'error': f'Invalid status. Valid: {valid}'}, status=400)

    prev = appt.status
    appt.status = new_s
    if new_s in ('COMPLETED','NO_SHOW'):
        appt.checked_out_at = timezone.now()
    appt.save()
    VisitorLog.objects.create(appointment=appt, actor=user,
        from_status=prev, to_status=new_s, notes=data.get('notes',''))

    if new_s == 'CANCELLED':
        from ..notifications import notify_appointment_cancelled
        notify_appointment_cancelled(appt)

    return JsonResponse({'appointment': _appt_to_dict(appt)})


@csrf_exempt
@_auth_required
@require_http_methods(['GET'])
def today_appointments(request):
    """Convenience — today's non-cancelled/completed appointments."""
    from ..models import VisitorAppointment
    today = timezone.now().date()
    user  = request.api_user
    from django.db.models import Q
    if user.is_staff or getattr(user,'is_gatekeeper',False):
        qs = VisitorAppointment.objects.filter(scheduled_date=today)
    else:
        qs = VisitorAppointment.objects.filter(
            scheduled_date=today
        ).filter(Q(host_user=user)|Q(host_department=user.department)|Q(booked_by=user)).distinct()
    qs = qs.exclude(status__in=['CANCELLED']).order_by('scheduled_start').select_related('host_user','host_department')
    return JsonResponse({'date': str(today), 'count': qs.count(),
                         'appointments': [_appt_to_dict(a) for a in qs]})


@csrf_exempt
@_auth_required
@require_http_methods(['GET'])
def user_list(request):
    """Staff/users list — for mobile app host selection."""
    from apps.accounts.models import User

    users = User.objects.filter(is_active=True).values(
        'id','first_name','last_name','email','department__name','department__id')
    return JsonResponse({'users': [
        {'id':u['id'],'name':f"{u['first_name']} {u['last_name']}".strip(),
         'email':u['email'],
         'department':{'id':u['department__id'],'name':u['department__name']}}
        for u in users
    ]})


@csrf_exempt
@_auth_required
@require_http_methods(['GET'])
def department_list(request):
    from apps.departments.models import Department
    depts = Department.objects.all().values('id','name','code')
    return JsonResponse({'departments': list(depts)})
