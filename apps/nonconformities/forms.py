
from django import forms
from .models import NonConformity
from apps.accounts.models import User, Site
from apps.departments.models import Department
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}; T={"class":"form-control","rows":3}
class NCForm(forms.ModelForm):
    class Meta:
        model=NonConformity
        fields=["title","category","severity","status","source","department","site",
                "description","requirement","root_cause","responsible_person","due_date","notes"]
        widgets={"title":forms.TextInput(attrs=C),"category":forms.Select(attrs=S),
            "severity":forms.Select(attrs=S),"status":forms.Select(attrs=S),
            "source":forms.TextInput(attrs=C),"department":forms.Select(attrs=S),
            "site":forms.Select(attrs=S),"description":forms.Textarea(attrs=T),
            "requirement":forms.Textarea(attrs=T),"root_cause":forms.Textarea(attrs=T),
            "responsible_person":forms.Select(attrs=S),"due_date":forms.DateInput(attrs=D),
            "notes":forms.Textarea(attrs=T)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["responsible_person"].required=False; self.fields["responsible_person"].empty_label="— Select person —"
        self.fields["responsible_person"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        self.fields["department"].required=False; self.fields["department"].empty_label="— All —"
        self.fields["site"].required=False; self.fields["site"].empty_label="— All —"
        for f in ["source","requirement","root_cause","due_date","notes"]: self.fields[f].required=False
