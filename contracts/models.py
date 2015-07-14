from django.db import models
from djorm_pgfulltext.models import SearchManager, SearchQuerySet
from djorm_pgfulltext.fields import VectorField


EDUCATION_CHOICES = (
    ('HS', 'High School'),
    ('AA', 'Associates'),
    ('BA', 'Bachelors'),
    ('MA', 'Masters'),
    ('PHD', 'Ph.D.'),
)


class CurrentContractManager(SearchManager):
    # need to subclass the SearchManager we were using for postgres full text search instead of default
    def get_queryset(self):
        return ContractsQuerySet(self.model, using=self._db)\
                .filter(current_price__gt=0)\
                .exclude(current_price__isnull=True)


class ContractsQuerySet(SearchQuerySet):

    def order_by(self, *args, **kwargs):
        edu_sort_sql = """
            case
                when education_level = 'HS' then 1
                when education_level = 'AA' then 2
                when education_level = 'BA' then 3
                when education_level = 'MA' then 4
                when education_level = 'PHD' then 5
                else -1
            end
        """

        edu_index = None

        sort_params = list(args)

        if 'education_level' in sort_params:
            edu_index = sort_params.index('education_level')
        elif '-education_level' in sort_params:
            edu_index = sort_params.index('-education_level')

        if edu_index is not None:
            sort_params[edu_index] = 'edu_sort' if not args[edu_index].startswith('-') else '-edu_sort'
            queryset = super(ContractsQuerySet, self)\
                .extra(select={'edu_sort': edu_sort_sql}, order_by=sort_params)
        else:
            queryset = super(ContractsQuerySet, self)\
                .order_by(*args, **kwargs)

        return queryset


class Contract(models.Model):

    idv_piid = models.CharField(max_length=128) #index this field
    piid = models.CharField(max_length=128) #index this field
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    contract_year = models.IntegerField(null=True, blank=True)
    vendor_name = models.CharField(max_length=128)
    labor_category = models.TextField(db_index=True)
    education_level = models.CharField(db_index=True, choices=EDUCATION_CHOICES, max_length=5, null=True, blank=True)
    min_years_experience = models.IntegerField(db_index=True)
    hourly_rate_year1 = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate_year2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contractor_site = models.CharField(db_index=True, max_length=128, null=True, blank=True)
    schedule = models.CharField(db_index=True, max_length=128, null=True, blank=True)
    business_size = models.CharField(db_index=True, max_length=128, null=True, blank=True)
    sin = models.TextField(null=True, blank=True)

    search_index = VectorField()

    #use a manager that filters by current contracts with a valid current_price
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
