from django import forms
from .models import Asset, AssetCategory
from apps.departments.models import Department
from apps.accounts.models import User


def _users(): return User.objects.filter(is_active=True).order_by("first_name","last_name")

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["asset_tag","name","category","brand","model_number","serial_number",
                  "description","status","condition","purchase_date","purchase_cost",
                  "purchase_order","warranty_expiry","department","allocated_to","location","notes"]
        widgets = {
            "asset_tag":forms.TextInput(attrs={"class":"form-control"}),
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "category":forms.Select(attrs={"class":"form-select"}),
            "brand":forms.TextInput(attrs={"class":"form-control"}),
            "model_number":forms.TextInput(attrs={"class":"form-control"}),
            "serial_number":forms.TextInput(attrs={"class":"form-control"}),
            "description":forms.Textarea(attrs={"class":"form-control","rows":2}),
            "status":forms.Select(attrs={"class":"form-select"}),
            "condition":forms.Select(attrs={"class":"form-select"}),
            "purchase_date":forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "purchase_cost":forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "purchase_order":forms.Select(attrs={"class":"form-select"}),
            "warranty_expiry":forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "department":forms.Select(attrs={"class":"form-select"}),
            "allocated_to":forms.Select(attrs={"class":"form-select"}),
            "location":forms.TextInput(attrs={"class":"form-control","placeholder":"e.g. Office 3B"}),
            "notes":forms.Textarea(attrs={"class":"form-control","rows":2}),
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["allocated_to"].required=False
        self.fields["allocated_to"].empty_label="— Unallocated —"
        self.fields["allocated_to"].queryset=_users()
        self.fields["department"].required=False
        self.fields["department"].empty_label="— No department —"
        self.fields["purchase_order"].required=False
        self.fields["purchase_order"].empty_label="— No linked PO —"
        from apps.purchase_orders.models import PurchaseOrder
        self.fields["purchase_order"].queryset=PurchaseOrder.objects.filter(
            status__in=["APPROVED","SENT_PROC","ORDERED","RECEIVED"]).order_by("-created_at")
        for f in ["serial_number","brand","model_number","description","purchase_date",
                  "purchase_cost","warranty_expiry","location","notes"]:
            self.fields[f].required=False

class AllocateForm(forms.Form):
    allocated_to = forms.ModelChoiceField(queryset=_users(), empty_label="— Select user —",
        label="Allocate To", widget=forms.Select(attrs={"class":"form-select"}))
    notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={"class":"form-control","rows":2,"placeholder":"Reason…"}))

class TransferForm(forms.Form):
    to_department = forms.ModelChoiceField(queryset=Department.objects.all(),
        empty_label="— Select department —", label="Transfer to Department",
        widget=forms.Select(attrs={"class":"form-select"}))
    notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={"class":"form-control","rows":2,"placeholder":"Reason…"}))

class OffboardForm(forms.Form):
    new_status = forms.ChoiceField(choices=[
        ("ACTIVE","Keep Active (return to dept pool)"),
        ("UNDER_REPAIR","Send for Repair"),("RETIRED","Retire"),("DISPOSED","Dispose"),
    ], label="After Offboarding", widget=forms.Select(attrs={"class":"form-select"}))
    notes = forms.CharField(required=True, label="Offboarding notes",
        widget=forms.Textarea(attrs={"class":"form-control","rows":2}))

class StatusChangeForm(forms.Form):
    status    = forms.ChoiceField(choices=Asset.Status.choices,
        widget=forms.Select(attrs={"class":"form-select"}))
    condition = forms.ChoiceField(choices=Asset.Condition.choices,
        widget=forms.Select(attrs={"class":"form-select"}))
    notes     = forms.CharField(required=False,
        widget=forms.Textarea(attrs={"class":"form-control","rows":2}))

class MutationNoteForm(forms.Form):
    notes = forms.CharField(label="Add Note",
        widget=forms.Textarea(attrs={"class":"form-control","rows":2,"placeholder":"Add a note…"}))
