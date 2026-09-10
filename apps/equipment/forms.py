
from django import forms
from .models import Equipment, EquipmentCategory
from apps.accounts.models import User, Site
from apps.departments.models import Department
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}; T={"class":"form-control","rows":2}
class EquipmentForm(forms.ModelForm):
    class Meta:
        model=Equipment
        fields=["asset_id","name","category","description","make","model_number","serial_number",
                "location","department","site","responsible_person","status","condition",
                "purchase_date","purchase_cost","warranty_expiry","last_inspection","next_inspection",
                "last_maintenance","next_maintenance","calibration_due","is_safety_critical","notes"]
        widgets={"asset_id":forms.TextInput(attrs=C),"name":forms.TextInput(attrs=C),
            "category":forms.Select(attrs=S),"description":forms.Textarea(attrs=T),
            "make":forms.TextInput(attrs=C),"model_number":forms.TextInput(attrs=C),
            "serial_number":forms.TextInput(attrs=C),"location":forms.TextInput(attrs=C),
            "department":forms.Select(attrs=S),"site":forms.Select(attrs=S),
            "responsible_person":forms.Select(attrs=S),"status":forms.Select(attrs=S),
            "condition":forms.Select(attrs=S),"purchase_cost":forms.NumberInput(attrs=C),
            "purchase_date":forms.DateInput(attrs=D),"warranty_expiry":forms.DateInput(attrs=D),
            "last_inspection":forms.DateInput(attrs=D),"next_inspection":forms.DateInput(attrs=D),
            "last_maintenance":forms.DateInput(attrs=D),"next_maintenance":forms.DateInput(attrs=D),
            "calibration_due":forms.DateInput(attrs=D),"notes":forms.Textarea(attrs=T)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["responsible_person"].required=False; self.fields["responsible_person"].empty_label="— Select person —"
        self.fields["responsible_person"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        self.fields["department"].required=False; self.fields["department"].empty_label="— All —"
        self.fields["site"].required=False; self.fields["site"].empty_label="— All —"
        for f in ["description","make","model_number","serial_number","location","purchase_date","purchase_cost",
                  "warranty_expiry","last_inspection","next_inspection","last_maintenance","next_maintenance",
                  "calibration_due","notes"]:
            self.fields[f].required=False
