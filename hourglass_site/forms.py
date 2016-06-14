from django import forms

class XlsForm(forms.Form):
    xls = forms.FileField(
        label="Proposed Price List (PPL) Excel file",
        required=True
    )
