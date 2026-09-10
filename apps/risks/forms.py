
from django import forms
from .models import RiskRegister
from apps.accounts.models import User, Site
from apps.departments.models import Department
WCLASS = {"class":"form-control"}
SCLASS = {"class":"form-select"}
TA = {"class":"form-control","rows":3}
class RiskForm(forms.ModelForm):
    class Meta:
        model=RiskRegister
        fields=["title","description","hazard_source","department","site",
                "likelihood","impact","controls","mitigation_plan","owner",
                "likelihood_residual","impact_residual","review_date","status","notes"]
        widgets={"title":forms.TextInput(attrs=WCLASS),"hazard_source":forms.TextInput(attrs=WCLASS),
            "description":forms.Textarea(attrs=TA),"controls":forms.Textarea(attrs=TA),
            "mitigation_plan":forms.Textarea(attrs=TA),"notes":forms.Textarea(attrs=TA),
            "department":forms.Select(attrs=SCLASS),"site":forms.Select(attrs=SCLASS),
            "likelihood":forms.Select(attrs=SCLASS),"impact":forms.Select(attrs=SCLASS),
            "likelihood_residual":forms.Select(attrs=SCLASS),"impact_residual":forms.Select(attrs=SCLASS),
            "owner":forms.Select(attrs=SCLASS),"status":forms.Select(attrs=SCLASS),
            "review_date":forms.DateInput(attrs={"class":"form-control","type":"date"})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["owner"].required=False; self.fields["owner"].empty_label="— Select owner —"
        self.fields["owner"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        self.fields["department"].required=False; self.fields["department"].empty_label="— All —"
        self.fields["site"].required=False; self.fields["site"].empty_label="— All —"
        for f in ["description","hazard_source","controls","mitigation_plan","notes",
                  "likelihood_residual","impact_residual","review_date"]:
            self.fields[f].required=False
