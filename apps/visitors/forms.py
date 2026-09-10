from django import forms
from django.utils import timezone
from .models import VisitorAppointment, WhatsAppConfig
from apps.departments.models import Department
from apps.accounts.models import User



class AppointmentForm(forms.ModelForm):
    class Meta:
        model  = VisitorAppointment
        fields = [
            'visitor_name', 'visitor_email', 'visitor_phone', 'visitor_company',
            'visitor_id_number', 'host_user', 'host_department',
            'scheduled_date', 'scheduled_start', 'scheduled_end',
            'agenda', 'vehicle_plate', 'vehicle_make', 'vehicle_colour', 'notes',
        ]
        widgets = {
            'visitor_name':      forms.TextInput(attrs={'class':'form-control','placeholder':'Full name'}),
            'visitor_email':     forms.EmailInput(attrs={'class':'form-control','placeholder':'visitor@example.com'}),
            'visitor_phone':     forms.TextInput(attrs={'class':'form-control','placeholder':'+254712345678'}),
            'visitor_company':   forms.TextInput(attrs={'class':'form-control','placeholder':'Company / Organisation'}),
            'visitor_id_number': forms.TextInput(attrs={'class':'form-control','placeholder':'National ID or Passport'}),
            'host_user':         forms.Select(attrs={'class':'form-select'}),
            'host_department':   forms.Select(attrs={'class':'form-select'}),
            'scheduled_date':    forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'scheduled_start':   forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'scheduled_end':     forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'agenda':            forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Purpose of visit / agenda (optional)'}),
            'vehicle_plate':     forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. KCA 001A'}),
            'vehicle_make':      forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Toyota Prado'}),
            'vehicle_colour':    forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Silver'}),
            'notes':             forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Any other notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['host_user'].required = False
        self.fields['host_user'].empty_label = '— Select staff member (if known) —'
        self.fields['host_user'].queryset = User.objects.filter(
            is_active=True).order_by('first_name', 'last_name')
        self.fields['host_department'].required = False
        self.fields['host_department'].empty_label = '— Select department (if host unknown) —'
        for f in ['visitor_email','visitor_phone','visitor_company','visitor_id_number',
                  'scheduled_end','agenda','vehicle_plate','vehicle_make','vehicle_colour','notes']:
            self.fields[f].required = False

    def clean(self):
        cd = super().clean()
        if not cd.get('host_user') and not cd.get('host_department'):
            raise forms.ValidationError(
                'Please select either a host staff member or a host department.')
        return cd


class ArrivalForm(forms.Form):
    """Used by gatekeeper to log arrival."""
    badge_number = forms.CharField(required=False, label='Visitor Badge Number',
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional badge/pass number'}))
    notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Any arrival notes'}))


class StatusUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ('ARRIVED',    'Arrived'),
        ('IN_MEETING', 'In Meeting'),
        ('COMPLETED',  'Completed / Checked Out'),
        ('NO_SHOW',    'No Show'),
        ('CANCELLED',  'Cancelled'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class':'form-select'}))
    notes  = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class':'form-control','rows':2}))


class WhatsAppConfigForm(forms.ModelForm):
    class Meta:
        model  = WhatsAppConfig
        fields = ['name','provider','account_sid','auth_token','from_number',
                  'api_url','api_key','extra_headers','is_active']
        widgets = {
            'name':         forms.TextInput(attrs={'class':'form-control'}),
            'provider':     forms.Select(attrs={'class':'form-select'}),
            'account_sid':  forms.TextInput(attrs={'class':'form-control'}),
            'auth_token':   forms.PasswordInput(attrs={'class':'form-control'},render_value=True),
            'from_number':  forms.TextInput(attrs={'class':'form-control','placeholder':'+12345678900'}),
            'api_url':      forms.TextInput(attrs={'class':'form-control','placeholder':'https://api.example.com/send'}),
            'api_key':      forms.PasswordInput(attrs={'class':'form-control'},render_value=True),
            'extra_headers':forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'{"X-Custom":"value"}'}),
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in ['account_sid','auth_token','from_number','api_url','api_key','extra_headers']:
            self.fields[f].required = False
