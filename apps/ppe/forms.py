
from django import forms
from .models import PPEItem, PPEType, PPERequirement
from apps.accounts.models import User
from apps.departments.models import Department
C={"class":"form-control"}; S={"class":"form-select"}; D={"class":"form-control","type":"date"}
class PPEItemForm(forms.ModelForm):
    class Meta:
        model=PPEItem
        fields=["ppe_type","item_code","brand","size","status","condition","purchase_date","expiry_date",
                "issued_to","issued_date","return_date","department","notes"]
        widgets={"ppe_type":forms.Select(attrs=S),"item_code":forms.TextInput(attrs=C),
            "brand":forms.TextInput(attrs=C),"size":forms.TextInput(attrs=C),
            "status":forms.Select(attrs=S),"condition":forms.Select(attrs=S),
            "purchase_date":forms.DateInput(attrs=D),"expiry_date":forms.DateInput(attrs=D),
            "issued_to":forms.Select(attrs=S),"issued_date":forms.DateInput(attrs=D),
            "return_date":forms.DateInput(attrs=D),"department":forms.Select(attrs=S),
            "notes":forms.Textarea(attrs={"class":"form-control","rows":2})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["issued_to"].required=False; self.fields["issued_to"].empty_label="— Not issued —"
        self.fields["issued_to"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        self.fields["department"].required=False; self.fields["department"].empty_label="— All —"
        for f in ["brand","size","purchase_date","expiry_date","issued_to","issued_date","return_date","notes"]:
            self.fields[f].required=False
