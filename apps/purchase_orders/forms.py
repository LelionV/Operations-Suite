from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseOrder, POLineItem


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                                 'placeholder': 'Optional overall description…'}),
        }


class POLineItemForm(forms.ModelForm):
    # Hidden fields populated by JS after QB item lookup
    qb_item_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = POLineItem
        fields = [
            'code', 'description', 'uom',
            'spec', 'quantity', 'purpose', 'photo', 'lead_time',
        ]
        widgets = {
            'code':        forms.TextInput(attrs={
                'class': 'form-control qb-code-input',
                'placeholder': 'Type to search QB items…',
                'autocomplete': 'off',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control', 'readonly': 'readonly',
                'placeholder': 'Auto-filled from QB item',
            }),
            'uom':         forms.TextInput(attrs={
                'class': 'form-control', 'readonly': 'readonly',
                'placeholder': 'Auto-filled from QB item',
            }),
            'spec':        forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Optional specification or notes…',
            }),
            'quantity':    forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'purpose':     forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Why is this item needed?',
            }),
            'photo':       forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'lead_time':   forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 3 days, 2 weeks',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['spec'].required = False
        self.fields['purpose'].required = False
        self.fields['photo'].required = False
        self.fields['lead_time'].required = False


POLineItemFormSet = inlineformset_factory(
    PurchaseOrder,
    POLineItem,
    form=POLineItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ApprovalForm(forms.Form):
    comment = forms.CharField(
        required=False,
        label='Comment (optional)',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                     'placeholder': 'Optional comment…'}),
    )


class RejectionForm(forms.Form):
    reason = forms.CharField(
        label='Rejection reason',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                     'placeholder': 'State the reason for rejection…'}),
    )


class ItemRejectionForm(forms.Form):
    item_ids = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label='Select items to reject',
    )
    reason = forms.CharField(
        label='Rejection reason',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                     'placeholder': 'Why are these items rejected?'}),
    )

    def __init__(self, *args, po=None, **kwargs):
        super().__init__(*args, **kwargs)
        if po:
            choices = [
                (item.pk, f'{item.code} — {item.description} (×{item.quantity})')
                for item in po.line_items.filter(is_rejected=False)
            ]
            self.fields['item_ids'].choices = choices
