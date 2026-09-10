
from django import forms
from .models import ComplianceRequirement
from apps.accounts.models import User
class ComplianceForm(forms.ModelForm):
    class Meta:
        model=ComplianceRequirement
        fields=["title","reference","category","description","applicable_to","owner","status","review_date","notes","is_active"]
        widgets={f:forms.TextInput(attrs={"class":"form-control"}) if f in ["title","reference","applicable_to"]
                 else forms.Select(attrs={"class":"form-select"}) if f in ["category","owner","status"]
                 else forms.Textarea(attrs={"class":"form-control","rows":3}) if f in ["description","notes"]
                 else forms.DateInput(attrs={"class":"form-control","type":"date"}) if f=="review_date"
                 else forms.CheckboxInput() for f in ["title","reference","category","description","applicable_to","owner","status","review_date","notes","is_active"]}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["owner"].required=False; self.fields["owner"].empty_label="— Select owner —"
        self.fields["owner"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        for f in ["description","applicable_to","review_date","notes"]: self.fields[f].required=False
