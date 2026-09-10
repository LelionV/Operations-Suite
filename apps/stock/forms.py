from django import forms
class StockUploadForm(forms.Form):
    file = forms.FileField(
        label='Stock Tracker File',
        help_text='Upload the Stock Analysis Report (.xlsx or .csv).',
        widget=forms.ClearableFileInput(attrs={'accept':'.xlsx,.xlsm,.csv','class':'form-control'}),
    )
