from contracts.models import Contract
from rest_framework import serializers, pagination

class ContractSerializer(serializers.ModelSerializer):

    education_level = serializers.CharField(source='get_education_level_display')

    class Meta:
        model = Contract
        fields = ('id', 'idv_piid', 'vendor_name', 'labor_category', 'education_level', 'min_years_experience', 'hourly_rate_year1', 'current_price', 'schedule', 'contractor_site', 'business_size')

class PaginatedContractSerializer(pagination.PaginationSerializer):

    average = serializers.SerializerMethodField()
    minimum = serializers.SerializerMethodField()
    maximum = serializers.SerializerMethodField()
    wage_histogram = serializers.SerializerMethodField()
    first_standard_deviation = serializers.SerializerMethodField()

    class Meta:
        object_serializer_class = ContractSerializer

    def get_average(self, obj):
        return self.context.get('average', 0)

    def get_minimum(self, obj):
        return self.context.get('minimum', 0)

    def get_maximum(self, obj):
        return self.context.get('maximum', 0)

    def get_wage_histogram(self, obj):
        return self.context.get('wage_histogram', [])

    def get_first_standard_deviation(self, obj):
        return self.context.get('first_standard_deviation', 0)
