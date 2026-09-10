from django import forms
from .models import Ticket, TicketComment
from apps.departments.models import Department


class TicketForm(forms.ModelForm):
    class Meta:
        model  = Ticket
        fields = ['title', 'description', 'department', 'priority',
                  'expected_resolution_date', 'purchase_order']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Brief summary of the issue…'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                  'placeholder': 'Describe the issue in detail…'}),
            'department':  forms.Select(attrs={'class': 'form-select'}),
            'priority':    forms.Select(attrs={'class': 'form-select'}),
            'expected_resolution_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'purchase_order': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purchase_order'].required = False
        self.fields['purchase_order'].empty_label = '— No linked PO —'
        self.fields['expected_resolution_date'].required = False
        self.fields['department'].empty_label = '— Select department —'
        self.fields['department'].required = True

        from apps.purchase_orders.models import PurchaseOrder
        self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(
            status__in=['APPROVED', 'SENT_PROC', 'ORDERED', 'RECEIVED']
        ).order_by('-created_at')


class TicketStatusForm(forms.ModelForm):
    """Used by HODs and permissioned users to update ticket status."""
    class Meta:
        model  = Ticket
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model  = TicketComment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment or update…',
            }),
        }
