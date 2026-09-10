
from django import forms
from .models import MaintenanceRecord
from apps.accounts.models import User
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}; T={"class":"form-control","rows":3}
class MaintenanceForm(forms.ModelForm):
    class Meta:
        model=MaintenanceRecord
        fields=["equipment","maintenance_type","title","description","service_provider","technician",
                "scheduled_date","completed_date","next_due_date","status","cost",
                "certificate_number","certificate_expiry","work_done","parts_used","assigned_to","notes"]
        widgets={"equipment":forms.Select(attrs=S),"maintenance_type":forms.Select(attrs=S),
            "title":forms.TextInput(attrs=C),"description":forms.Textarea(attrs=T),
            "service_provider":forms.TextInput(attrs=C),"technician":forms.TextInput(attrs=C),
            "scheduled_date":forms.DateInput(attrs=D),"completed_date":forms.DateInput(attrs=D),
            "next_due_date":forms.DateInput(attrs=D),"status":forms.Select(attrs=S),
            "cost":forms.NumberInput(attrs=C),"certificate_number":forms.TextInput(attrs=C),
            "certificate_expiry":forms.DateInput(attrs=D),"work_done":forms.Textarea(attrs=T),
            "parts_used":forms.Textarea(attrs=T),"assigned_to":forms.Select(attrs=S),"notes":forms.Textarea(attrs=T)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["assigned_to"].required=False; self.fields["assigned_to"].empty_label="— Unassigned —"
        self.fields["assigned_to"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        for f in ["description","service_provider","technician","completed_date","next_due_date","cost",
                  "certificate_number","certificate_expiry","work_done","parts_used","notes"]:
            self.fields[f].required=False
