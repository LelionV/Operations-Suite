from django import forms


class QBUploadForm(forms.Form):
    file = forms.FileField(
        label='QB Items file (CSV or XLSX)',
        help_text='Required columns: Code, Description, UOM',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'}),
    )
