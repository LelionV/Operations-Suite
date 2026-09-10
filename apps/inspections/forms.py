
from django import forms
from .models import Inspection
from apps.accounts.models import User, Site
from apps.departments.models import Department
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}; T={"class":"form-control","rows":3}
class InspectionForm(forms.ModelForm):
    class Meta:
        model=Inspection
        fields=["title","inspection_type","checklist","equipment","department","site","inspector",
                "scheduled_date","next_inspection_date","status","summary","defects_found","notes"]
        widgets={"title":forms.TextInput(attrs=C),"inspection_type":forms.Select(attrs=S),
            "checklist":forms.Select(attrs=S),"equipment":forms.Select(attrs=S),
            "department":forms.Select(attrs=S),"site":forms.Select(attrs=S),
            "inspector":forms.Select(attrs=S),"status":forms.Select(attrs=S),
            "scheduled_date":forms.DateInput(attrs=D),"next_inspection_date":forms.DateInput(attrs=D),
            "summary":forms.Textarea(attrs=T),"defects_found":forms.Textarea(attrs=T),"notes":forms.Textarea(attrs=T)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["inspector"].required=False; self.fields["inspector"].empty_label="— Select inspector —"
        self.fields["inspector"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        for f in ["checklist","equipment","department","site","next_inspection_date","summary","defects_found","notes"]:
            self.fields[f].required=False
        self.fields["department"].empty_label="— All —"; self.fields["site"].empty_label="— All —"
        self.fields["checklist"].empty_label="— No checklist —"; self.fields["equipment"].empty_label="— No equipment —"
