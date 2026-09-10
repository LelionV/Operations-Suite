
from django import forms
from .models import PolicyDocument
from apps.accounts.models import User
from apps.departments.models import Department

class PolicyForm(forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["title","doc_number","doc_type","version","status","description",
                  "file","approved_by","review_date","expiry_date","departments",
                  "requires_acknowledgement"]
        widgets = {
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "doc_number":forms.TextInput(attrs={"class":"form-control"}),
            "doc_type":forms.Select(attrs={"class":"form-select"}),
            "version":forms.TextInput(attrs={"class":"form-control"}),
            "status":forms.Select(attrs={"class":"form-select"}),
            "description":forms.Textarea(attrs={"class":"form-control","rows":3}),
            "file":forms.ClearableFileInput(attrs={"class":"form-control"}),
            "approved_by":forms.Select(attrs={"class":"form-select"}),
            "review_date":forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "expiry_date":forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "departments":forms.SelectMultiple(attrs={"class":"form-select","size":"5"}),
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["approved_by"].required=False; self.fields["approved_by"].empty_label="— Select approver —"
        self.fields["approved_by"].queryset=User.objects.filter(is_active=True).order_by("first_name")
        for f in ["description","file","approved_by","review_date","expiry_date"]:
            self.fields[f].required=False
        self.fields["departments"].required=False
