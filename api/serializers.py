from contracts.models import Contract
from rest_framework import serializers


class ContractSerializer(serializers.ModelSerializer):

    education_level = serializers.CharField(source='get_education_level_display')

    class Meta:
        model = Contract
        fields = ('id', 'idv_piid', 'vendor_name', 'labor_category', 'education_level', 'min_years_experience', 'hourly_rate_year1', 'current_price', 'next_year_price', 'second_year_price', 'schedule', 'contractor_site', 'business_size')
