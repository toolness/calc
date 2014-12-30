from django.db import models
from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField


EDUCATION_CHOICES = (
    ('HS', 'High School'),
    ('AA', 'Associates'),
    ('BA', 'Bachelors'),
    ('MA', 'Masters'),
    ('PHD', 'Ph.D.'),
)


class CurrentContractManager(SearchManager):
    #need to subclass the SearchManager we were using for postgres full text search instead of default
    def get_queryset(self):
        return super(CurrentContractManager, self).get_queryset().filter(current_price__gt=0).exclude(current_price__isnull=True)

class Contract(models.Model):

    idv_piid = models.CharField(max_length=128) #index this field
    piid = models.CharField(max_length=128) #index this field
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    vendor_name = models.CharField(max_length=128)
    labor_category = models.TextField() #index this field
    education_level = models.CharField(choices=EDUCATION_CHOICES, max_length=5, null=True, blank=True)
    min_years_experience = models.IntegerField()
    hourly_rate_year1 = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate_year2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contractor_site = models.CharField(max_length=128, null=True, blank=True)
    schedule = models.CharField(max_length=128, null=True, blank=True)
    business_size = models.CharField(max_length=128, null=True, blank=True)
    sin = models.TextField(null=True, blank=True)

    search_index = VectorField()

    #use a manager that filters by current contracts with a valud current_price
    objects = CurrentContractManager(
        fields=('labor_category',),
        config = 'pg_catalog.english',
        search_field='search_index',
        auto_update_search_field = True
    )

    def get_readable_business_size(self):
        if 's' in self.business_size.lower():
            return 'small business'
        else:
            return 'other than small business'

    def get_education_code(self, text):
        
        for pair in EDUCATION_CHOICES:
            if text.strip() in pair[1]:
                return pair[0]

        return None

    def normalize_rate(self, rate):
        return float(rate.replace(',', '').replace('$', ''))
