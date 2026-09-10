
from django import forms
from .models import TrainingRecord, TrainingCourse
from apps.accounts.models import User
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}; T={"class":"form-control","rows":2}
class TrainingForm(forms.ModelForm):
    class Meta:
        model=TrainingRecord
        fields=["employee","course","status","scheduled_date","completed_date","expiry_date",
                "score","pass_mark","certificate_number","certificate_file","trainer","notes"]
        widgets={"employee":forms.Select(attrs=S),"course":forms.Select(attrs=S),
            "status":forms.Select(attrs=S),"scheduled_date":forms.DateInput(attrs=D),
            "completed_date":forms.DateInput(attrs=D),"expiry_date":forms.DateInput(attrs=D),
            "score":forms.NumberInput(attrs=C),"pass_mark":forms.NumberInput(attrs=C),
            "certificate_number":forms.TextInput(attrs=C),
            "certificate_file":forms.ClearableFileInput(attrs=C),
            "trainer":forms.TextInput(attrs=C),"notes":forms.Textarea(attrs=T)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["employee"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        for f in ["completed_date","expiry_date","score","certificate_number","certificate_file","trainer","notes"]:
            self.fields[f].required=False
