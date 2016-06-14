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
    contractor_site = forms.CharField(
        label="Worksite",
        required=True
        # TODO: Validate this is customer, contractor, or both.
    )
    contract_year = forms.IntegerField(
        label="Current contract year",
        required=True
        # TODO: Ensure this is between 1 and 5.
    )
    contract_start = forms.CharField(
        label="Contract start date",
        required=True
        # TODO: Make this a date field.
    )
    contract_end = forms.CharField(
        label="Contract end date",
        required=True
        # TODO: Make this a date field.
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
