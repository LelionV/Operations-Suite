from django import forms
from .models import ProcurementOrder


class ProcurementOrderForm(forms.ModelForm):
    """All fields optional — procurement officer fills what they know."""
    class Meta:
        model  = ProcurementOrder
        fields = ['supplier_name', 'supplier_contact', 'supplier_email',
                  'order_reference', 'expected_delivery', 'notes']
        widgets = {
            'supplier_name':     forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': 'Supplier name (optional)'}),
            'supplier_contact':  forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': 'Contact person'}),
            'supplier_email':    forms.EmailInput(attrs={'class': 'form-control',
                                                         'placeholder': 'supplier@email.com'}),
            'order_reference':   forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': 'Invoice / LPO reference'}),
            'expected_delivery': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':             forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                                       'placeholder': 'Any notes…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.required = False
