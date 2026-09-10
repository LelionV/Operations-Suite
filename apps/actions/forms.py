
from django import forms
from .models import Action
from apps.accounts.models import User
from apps.departments.models import Department
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}; T={"class":"form-control","rows":3}
class ActionForm(forms.ModelForm):
    class Meta:
        model=Action
        fields=["title","action_type","priority","status","source","description","root_cause",
                "action_plan","owner","department","due_date","completed_date",
                "evidence","evidence_file","notes"]
        widgets={"title":forms.TextInput(attrs=C),"action_type":forms.Select(attrs=S),
            "priority":forms.Select(attrs=S),"status":forms.Select(attrs=S),
            "source":forms.TextInput(attrs=C),"description":forms.Textarea(attrs=T),
            "root_cause":forms.Textarea(attrs=T),"action_plan":forms.Textarea(attrs=T),
            "owner":forms.Select(attrs=S),"department":forms.Select(attrs=S),
            "due_date":forms.DateInput(attrs=D),"completed_date":forms.DateInput(attrs=D),
            "evidence":forms.Textarea(attrs=T),"evidence_file":forms.ClearableFileInput(attrs=C),
            "notes":forms.Textarea(attrs=T)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["owner"].required=False; self.fields["owner"].empty_label="— Select owner —"
        self.fields["owner"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        self.fields["department"].required=False; self.fields["department"].empty_label="— All —"
        for f in ["source","root_cause","action_plan","due_date","completed_date","evidence","evidence_file","notes"]:
            self.fields[f].required=False
