from django import forms

class XlsForm(forms.Form):
    xls = forms.FileField(
        label="Proposed Price List (PPL) Excel file",
        required=True
    )

class ContractDetailsForm(forms.Form):
    idv_piid = forms.CharField(
        label="Contract number",
        required=True
    )
    vendor_name = forms.CharField(
        label="Vendor name"
    )
    business_size = forms.CharField(
        label="Business size"
    )
    schedule = forms.CharField(
        label="Schedule"
    )
    contractor_site = forms.ChoiceField(
        label="Worksite",
        required=True,
        choices=[
            ('customer', 'customer'),
            ('contractor', 'contractor'),
            ('both', 'both')
        ]
    )
    contract_year = forms.IntegerField(
        label="Current contract year",
        required=True,
        min_value=1,
        max_value=5
    )
    contract_start = forms.DateField(
        label="Contract start date",
        required=True
    )
    contract_end = forms.DateField(
        label="Contract end date",
        required=True
    )


class ProposedPriceListRow(forms.Form):
    sin = forms.CharField(
        label="SIN",
        required=True
    )
    labor_category = forms.CharField(
        label="Service proposed",
        required=True
    )
    education_level = forms.CharField(
        label="Minimum education / certification level",
        required=True
        # TODO: validate this is Associates, Bachelors, Masters, or Ph.D.
    )
    min_years_experience = forms.IntegerField(
        label="Minimum years of experience",
        required=True
    )
    current_price = forms.DecimalField(
        label="Price offered to GSA (including IFF)",
        required=True
    )
