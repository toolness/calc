from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Avg, Max, Min, Count
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import PaginatedContractSerializer
from contracts.models import Contract, EDUCATION_CHOICES

try: 
    #python2 compat
    import unicodecsv as csv
except:
    import csv

def convert_to_tsquery(query):
    #converts multi-word phrases into AND boolean queries for postgresql
    tsquery = query.strip() + ':*'
    if ' ' in tsquery:
        words = tsquery.split(' ')
        tsquery = ' & '.join(words)

    return tsquery

def get_contracts_queryset(request_params, wage_field):

    query = request_params.get('q', None)
    min_experience = request_params.get('min_experience', 0)
    max_experience = request_params.get('max_experience', 100)
    min_education = request_params.get('min_education', None)
    schedule = request_params.get('schedule', None)
    site = request_params.get('site', None)
    business_size = request_params.get('business_size', None)
    price = request_params.get('price', None)
    price__gt = request_params.get('price__gt')
    price__lt = request_params.get('price__lt')

    contracts = Contract.objects.filter(min_years_experience__gte=min_experience, min_years_experience__lte=max_experience).order_by(wage_field)

    if query:
        query = convert_to_tsquery(query)
        contracts = contracts.search(query, raw=True)

    if min_education:
        for index, pair in enumerate(EDUCATION_CHOICES):
            if min_education == pair[0]:
                contracts = contracts.filter(education_level__in=[ed[0] for ed in EDUCATION_CHOICES[index:] ])

    if schedule:
        contracts = contracts.filter(schedule__iexact=schedule)
    if site:
        contracts = contracts.filter(contractor_site__icontains=site)
    if business_size == 's':
        contracts = contracts.filter(business_size__icontains='s')
    elif business_size == 'o':
        contracts = contracts.filter(business_size__icontains='o')
    if price:
        contracts = contracts.filter(**{wage_field + '__exact': price})
    elif price__gt:
        contracts = contracts.filter(**{wage_field + '__gt': price__gt})
    elif price__lt:
        contracts = contracts.filter(**{wage_field + '__lt': price__lt})

    return contracts


class GetRates(APIView):

    def get(self, request):

        page = request.QUERY_PARAMS.get('page', 1)
        wage_field = 'current_price'
        contracts_all = self.get_queryset(request.QUERY_PARAMS, wage_field)
        page_stats = {}

        if contracts_all:
            page_stats['average'] = Decimal(contracts_all.aggregate(Avg(wage_field))[wage_field + '__avg']).quantize(Decimal(10) ** -2)
            page_stats['minimum'] = contracts_all.aggregate(Min(wage_field))[wage_field + '__min']
            page_stats['maximum'] = contracts_all.aggregate(Max(wage_field))[wage_field + '__max']
            hourly_wage_stats = contracts_all.values('min_years_experience').annotate(average_wage=Avg(wage_field), min_wage=Min(wage_field), max_wage=Max(wage_field), num_contracts=Count('sin')).order_by()

            #Avg always returns float, so make it a fixed point string in each dict
            for item in hourly_wage_stats:
                item['average_wage'] = Decimal(item['average_wage']).quantize(Decimal(10) ** -2)

            page_stats['hourly_wage_stats'] = sorted(hourly_wage_stats, key=lambda mye: mye['min_years_experience'])

            paginator = Paginator(contracts_all, settings.PAGINATION)
            contracts = paginator.page(page)
            serializer = PaginatedContractSerializer(contracts, context=page_stats)

            return Response(serializer.data)

        else:
            return Response({'count': 0, 'results': []})

    def get_queryset(self, request, wage_field):
        return get_contracts_queryset(request, wage_field)

def get_rates_csv(request):
        
    wage_field = 'current_price'
    contracts_all = get_contracts_queryset(request.GET, wage_field)
    
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="pricing_results.csv"'
    writer = csv.writer(response) 
    writer.writerow(("Contract #", "Business Size", "Schedule", "Site", "Begin Date", "End Date", "SIN", "Vendor Name", "Labor Category", "education Level", "Minimum Years Experience", "Current Year Labor Price"))

    for c in contracts_all:
        writer.writerow((c.idv_piid, c.get_readable_business_size(), c.schedule, c.contractor_site, c.contract_start, c.contract_end, c.sin, c.vendor_name, c.labor_category, c.get_education_level_display(), c.min_years_experience, c.current_price ))
    
    return response

class GetAutocomplete(APIView):

    def get(self, request, format=None):
        q = request.QUERY_PARAMS.get('q', False)

        if q:
            data = Contract.objects.search(convert_to_tsquery(q), raw=True).values('labor_category').annotate(count=Count('labor_category')).order_by('-count')
            return Response(data)




