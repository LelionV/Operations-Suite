from django import forms
from django.forms import inlineformset_factory
from .models import GoodsReceivedNote, GRNLineItem


class GRNForm(forms.ModelForm):
    class Meta:
        model  = GoodsReceivedNote
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                           'placeholder': 'General notes about this delivery…'}),
        }


class GRNLineItemForm(forms.ModelForm):
    # Display-only fields rendered in the template manually
    code        = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}))
    description = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}))
    uom         = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}))
    qty_ordered = forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}))

    class Meta:
        model  = GRNLineItem
        fields = ['po_line_item', 'qty_received', 'condition', 'notes']
        widgets = {
            'po_line_item': forms.HiddenInput(),
            'qty_received': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'condition':    forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'e.g. Good, Damaged'}),
            'notes':        forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Item-level note…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill display fields from the linked PO line item
        li = None
        if self.instance and self.instance.pk:
            li = self.instance.po_line_item
        elif self.initial.get('po_line_item'):
            li = self.initial['po_line_item']
        if li:
            self.fields['code'].initial        = li.code
            self.fields['description'].initial = li.description
            self.fields['uom'].initial         = li.uom
            self.fields['qty_ordered'].initial = li.quantity


GRNLineItemFormSet = inlineformset_factory(
    GoodsReceivedNote,
    GRNLineItem,
    form=GRNLineItemForm,
    extra=0,
    can_delete=False,
)
