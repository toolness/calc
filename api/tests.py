from django.test import TestCase, Client
from model_mommy import mommy
from model_mommy.recipe import seq
from contracts.models import Contract
from contracts.mommy_recipes import get_contract_recipe
from api.views import convert_to_tsquery

from itertools import cycle

class ContractsTest(TestCase):
    """ tests for the /api/rates endpoint """
    BUSINESS_SIZES = ('small business', 'other than small business')

    def setUp(self):
        # unittest config
        self.maxDiff=None
        self.longMessage=True

        self.c = Client()
        self.path = '/api/rates/'

    def test_convert_to_tsquery(self):
        self.assertEqual(convert_to_tsquery('staff  consultant'), 'staff:* & consultant:*')
        self.assertEqual(convert_to_tsquery('senior typist (st)'), 'senior:* & typist:* & st:*')
        self.assertEqual(convert_to_tsquery('@$(#)%&**#'), '')

    def test_empty_results(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'nsfr87y3487h3rufbf'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_search_results(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'accounting'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC234',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Accounting, CPA',
           'education_level': 'Masters',
           'min_years_experience': 5,
           'hourly_rate_year1': 50.0,
           'current_price': 50.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_multi_word_search_results__hit(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'legal services'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_multi_word_search_results__miss(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'legal advice'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_multi_category_search_results(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'legal services, accounting'})
        self.assertEqual(resp.status_code, 200)
        self.assertResultsEqual(resp.data['results'],
           [{'id': 1,
            'idv_piid': 'ABC123',
            'vendor_name': 'ACME Corp.',
            'labor_category': 'Legal Services',
            'education_level': None,
            'min_years_experience': 10,
            'hourly_rate_year1': 18.0,
            'current_price': 18.0,
            'schedule': None,
            'contractor_site': None,
            'business_size': None},
            {'id': 2,
            'idv_piid': 'ABC234',
            'vendor_name': 'Numbers R Us',
            'labor_category': 'Accounting, CPA',
            'education_level': 'Masters',
            'min_years_experience': 5,
            'hourly_rate_year1': 50.0,
            'current_price': 50.0,
            'schedule': None,
            'contractor_site': None,
            'business_size': None}])

    def test_search_results_with_nonalphanumeric(self):
        # the search should be able to handle queries with non-alphanumeric chars without erroring
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'category (ABC)"^$#@!&*'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_search_results_with_extra_spaces(self):
        # the search should insert the correct number of ampersands in the right locations
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'legal  advice '})
        self.assertEqual(resp.status_code, 200)

    def test_filter_by_price__exact(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price': 18})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_price__gte(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price__gte': 20})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC234',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Accounting, CPA',
           'education_level': 'Masters',
           'min_years_experience': 5,
           'hourly_rate_year1': 50.0,
           'current_price': 50.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_price__lte(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price__lte': 16})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC345',
           'vendor_name': 'Word Power Co.',
           'labor_category': 'Writer/Editor',
           'education_level': 'Bachelors',
           'min_years_experience': 1,
           'hourly_rate_year1': 16.0,
           'current_price': 16.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_price__gte_and_lte(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price__lte': 20, 'price__gte': 18})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_min_education(self):
        get_contract_recipe().make(_quantity=5, education_level=cycle(['MA', 'HS', 'BA', 'AA', 'PHD']))
        resp = self.c.get(self.path, {'min_education': 'AA', 'sort': 'education_level'})
        self.assertEqual(resp.status_code, 200)

        # if this is working properly, it does not include HS in the results
        self.assertResultsEqual(resp.data['results'], [
            {  'idv_piid': 'ABC1234',
               'education_level': 'Associates' },
            {  'idv_piid': 'ABC1233',
               'education_level': 'Bachelors' },
            {  'idv_piid': 'ABC1231',
               'education_level': 'Masters' },
            {  'idv_piid': 'ABC1235',
               'education_level': 'Ph.D.' },
           ], True)

    def test_filter_by_education_single(self):
        get_contract_recipe().make(_quantity=5, education_level=cycle(['MA', 'HS', 'BA', 'AA', 'PHD']))
        resp = self.c.get(self.path, {'education': 'AA', 'sort': 'education_level'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'], [
            { 'idv_piid': 'ABC1234',
              'education_level': 'Associates' }
            ], True)

    def test_filter_by_education_multiple(self):
        get_contract_recipe().make(_quantity=5, education_level=cycle(['MA', 'HS', 'BA', 'AA', 'PHD']))
        resp = self.c.get(self.path, {'education': 'AA,MA,PHD', 'sort': 'education_level'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'], [
            { 'idv_piid': 'ABC1234',
              'education_level': 'Associates' },
            {  'idv_piid': 'ABC1231',
               'education_level': 'Masters' },
            {  'idv_piid': 'ABC1235',
               'education_level': 'Ph.D.' },
            ], True)

    def test_sort_by_education_level(self):
        # deliberately placing education level cycle out of order so that proper ordering cannot be
        # a side-effect of ordering by idv_piid or another serially-generated field
        get_contract_recipe().make(_quantity=5, education_level=cycle(['MA', 'HS', 'BA', 'AA', 'PHD']))

        resp = self.c.get(self.path, {'sort': 'education_level'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'], [
            {   'idv_piid': 'ABC1232',
                'vendor_name': 'CompanyName2',
                'labor_category': 'Business Analyst II',
                'education_level': 'High School',
                'min_years_experience': 7,
                'hourly_rate_year1': 22.0,
                'current_price': 22.00,
                'schedule': 'PES',
                'contractor_site': None,
                'business_size': None},
           {   'idv_piid': 'ABC1234',
                'vendor_name': 'CompanyName4',
                'labor_category': 'Business Analyst II',
                'education_level': 'Associates',
                'min_years_experience': 9,
                'hourly_rate_year1': 24.0,
                'current_price': 24.0,
                'schedule': 'PES',
                'contractor_site': None,
                'business_size': None},
            {   'idv_piid': 'ABC1233',
                'vendor_name': 'CompanyName3',
                'labor_category': 'Business Analyst II',
                'education_level': 'Bachelors',
                'min_years_experience': 8,
                'hourly_rate_year1': 23.0,
                'current_price': 23.0,
                'schedule': 'MOBIS',
                'contractor_site': None,
                'business_size': None},
            {   'idv_piid': 'ABC1231',
                'vendor_name': 'CompanyName1',
                'labor_category': 'Business Analyst II',
                'education_level': 'Masters',
                'min_years_experience': 6,
                'hourly_rate_year1': 21.0,
                'current_price': 21.0,
                'schedule': 'MOBIS',
                'contractor_site': None,
                'business_size': None},
            {   'idv_piid': 'ABC1235',
                'vendor_name': 'CompanyName5',
                'labor_category': 'Business Analyst II',
                'education_level': 'Ph.D.',
                'min_years_experience': 10,
                'hourly_rate_year1': 25.0,
                'current_price': 25.0,
                'schedule': 'MOBIS',
                'contractor_site': None,
                'business_size': None},
        ])

    def test_sort_by_education_level__asc(self):
        # deliberately placing education level cycle out of order so that proper ordering cannot be
        # a side-effect of ordering by idv_piid or another serially-generated field
        get_contract_recipe().make(_quantity=5, education_level=cycle(['MA', 'HS', 'BA', 'AA', 'PHD']))

        resp = self.c.get(self.path, {'sort': '-education_level'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'], [
            {   'idv_piid': 'ABC1235',
                'vendor_name': 'CompanyName5',
                'labor_category': 'Business Analyst II',
                'education_level': 'Ph.D.',
                'min_years_experience': 10,
                'hourly_rate_year1': 25.0,
                'current_price': 25.0,
                'schedule': 'MOBIS',
                'contractor_site': None,
                'business_size': None},
            {   'idv_piid': 'ABC1231',
                'vendor_name': 'CompanyName1',
                'labor_category': 'Business Analyst II',
                'education_level': 'Masters',
                'min_years_experience': 6,
                'hourly_rate_year1': 21.0,
                'current_price': 21.0,
                'schedule': 'MOBIS',
                'contractor_site': None,
                'business_size': None},
            {   'idv_piid': 'ABC1233',
                'vendor_name': 'CompanyName3',
                'labor_category': 'Business Analyst II',
                'education_level': 'Bachelors',
                'min_years_experience': 8,
                'hourly_rate_year1': 23.0,
                'current_price': 23.0,
                'schedule': 'MOBIS',
                'contractor_site': None,
                'business_size': None},
           {   'idv_piid': 'ABC1234',
                'vendor_name': 'CompanyName4',
                'labor_category': 'Business Analyst II',
                'education_level': 'Associates',
                'min_years_experience': 9,
                'hourly_rate_year1': 24.0,
                'current_price': 24.0,
                'schedule': 'PES',
                'contractor_site': None,
                'business_size': None},
            {   'idv_piid': 'ABC1232',
                'vendor_name': 'CompanyName2',
                'labor_category': 'Business Analyst II',
                'education_level': 'High School',
                'min_years_experience': 7,
                'hourly_rate_year1': 22.0,
                'current_price': 22.00,
                'schedule': 'PES',
                'contractor_site': None,
                'business_size': None},
        ])

    def test_sort_by_education_level__retains_all_sort_params(self):
        # placing education level and price cycles out of phase so that sort precedence matters
        get_contract_recipe().make(_quantity=9, vendor_name='ServicesRUs', current_price=cycle([15.0, 10.0]), education_level=cycle(['BA', 'HS', 'AA']))

        resp = self.c.get(self.path, {'sort': 'current_price,education_level,-idv_piid'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'], [
            {   'idv_piid': 'ABC1238',
                'education_level': 'High School',
                'current_price': 10.0},
            {   'idv_piid': 'ABC1232',
                'education_level': 'High School',
                'current_price': 10.0},
            {   'idv_piid': 'ABC1236',
                'education_level': 'Associates',
                'current_price': 10.0},
            {   'idv_piid': 'ABC1234',
                'education_level': 'Bachelors',
                'current_price': 10.0},
            {   'idv_piid': 'ABC1235',
                'education_level': 'High School',
                'current_price': 15.0},
            {   'idv_piid': 'ABC1239',
                'education_level': 'Associates',
                'current_price': 15.0},
            {   'idv_piid': 'ABC1233',
                'education_level': 'Associates',
                'current_price': 15.0},
            {   'idv_piid': 'ABC1237',
                'education_level': 'Bachelors',
                'current_price': 15.0},
            {   'idv_piid': 'ABC1231',
                'education_level': 'Bachelors',
                'current_price': 15.0},
        ], just_expected_fields=True)

    def test_filter_by_min_experience(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'min_experience': '8'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_year_out(self):
        get_contract_recipe().make(_quantity=1)
        resp = self.c.get(self.path, {'current-year': '2'})
        self.assertEqual(resp.status_code, 200)

        self.prettyPrint(resp.data['results'])
        self.assertResultsEqual(resp.data['results'],
         [{'id': 28,
          'idv_piid': 'ABC1231',
          'vendor_name': 'CompanyName1',
          'labor_category': 'Business Analyst II',
          'education_level': None,
          'min_years_experience': 6,
          'hourly_rate_year1': 21.00,
          'current_price': 21.00,
          'next_year_price': 31.00,
          'second_year_price': 41.00,
          'schedule': 'MOBIS',
          'contractor_site': None,
          'business_size': None}])

    def test_filter_by_max_experience(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'max_experience': '3'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC345',
           'vendor_name': 'Word Power Co.',
           'labor_category': 'Writer/Editor',
           'education_level': 'Bachelors',
           'min_years_experience': 1,
           'hourly_rate_year1': 16.0,
           'current_price': 16.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_experience_range(self):
        get_contract_recipe().make(_quantity=3)
        resp = self.c.get(self.path, {'experience_range': '6,8'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC1231',
           'vendor_name': 'CompanyName1',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC1232',
           'vendor_name': 'CompanyName2',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 7,
           'hourly_rate_year1': 22.0,
           'current_price': 22.0,
           'schedule': 'PES',
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC1233',
           'vendor_name': 'CompanyName3',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 8,
           'hourly_rate_year1': 23.0,
           'current_price': 23.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_experience_single(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'experience_range': '10'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_schedule(self):
        get_contract_recipe().make(_quantity=3)
        resp = self.c.get(self.path, {'schedule': 'MOBIS'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC1231',
           'vendor_name': 'CompanyName1',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC1233',
           'vendor_name': 'CompanyName3',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 8,
           'hourly_rate_year1': 23.0,
           'current_price': 23.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_business_size(self):
        get_contract_recipe().make(_quantity=3, business_size=cycle(self.BUSINESS_SIZES))
        resp = self.c.get(self.path, {'business_size': 's'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC1231',
           'vendor_name': 'CompanyName1',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': 'small business'},
         {'idv_piid': 'ABC1233',
           'vendor_name': 'CompanyName3',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 8,
           'hourly_rate_year1': 23.0,
           'current_price': 23.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': 'small business'}])

        resp = self.c.get(self.path, {'business_size': 'o'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC1232',
           'vendor_name': 'CompanyName2',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 7,
           'hourly_rate_year1': 22.0,
           'current_price': 22.0,
           'schedule': 'PES',
           'contractor_site': None,
           'business_size': 'other than small business'}]
         )

        resp = self.c.get(self.path, {'business_size': 's', 'sort': '-current_price'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC1233',
           'vendor_name': 'CompanyName3',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 8,
           'hourly_rate_year1': 23.0,
           'current_price': 23.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': 'small business'},
         {'idv_piid': 'ABC1231',
           'vendor_name': 'CompanyName1',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': 'small business'}])

    def test_sort_on_multiple_columns(self):
        self.make_test_set()
        # make one more with the same vendor name, so we can see the secondary sort on price
        get_contract_recipe().make(_quantity=1, vendor_name='Numbers R Us')

        resp = self.c.get(self.path, {'sort': '-vendor_name,current_price'})

        self.assertEqual(resp.status_code, 200)
        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC345',
           'vendor_name': 'Word Power Co.',
           'labor_category': 'Writer/Editor',
           'education_level': 'Bachelors',
           'min_years_experience': 1,
           'hourly_rate_year1': 16.0,
           'current_price': 16.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC1231',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC234',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Accounting, CPA',
           'education_level': 'Masters',
           'min_years_experience': 5,
           'hourly_rate_year1': 50.0,
           'current_price': 50.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

        # sort the price descending, too, to make sure we're not just randomly passing the first test
        resp = self.c.get(self.path, {'sort': '-vendor_name,-current_price'})

        self.assertEqual(resp.status_code, 200)
        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC345',
           'vendor_name': 'Word Power Co.',
           'labor_category': 'Writer/Editor',
           'education_level': 'Bachelors',
           'min_years_experience': 1,
           'hourly_rate_year1': 16.0,
           'current_price': 16.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC234',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Accounting, CPA',
           'education_level': 'Masters',
           'min_years_experience': 5,
           'hourly_rate_year1': 50.0,
           'current_price': 50.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC1231',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_query_type__match_phrase(self):
        self.make_test_set()
        get_contract_recipe().make(_quantity=1, labor_category='Professional Legal Services I')
        resp = self.c.get(self.path, {'q': 'legal services', 'query_type': 'match_phrase'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None},
          {'idv_piid': 'ABC1231',
           'vendor_name': 'CompanyName1',
           'labor_category': 'Professional Legal Services I',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None}])

    def test_query_type__match_exact(self):
        self.make_test_set()
        get_contract_recipe().make(_quantity=1, labor_category='Professional Legal Services I')
        resp = self.c.get(self.path, {'q': 'legal services', 'query_type': 'match_exact'})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 10,
           'hourly_rate_year1': 18.0,
           'current_price': 18.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_minimum_price_no_args(self):
        self.make_test_set()
        resp = self.c.get(self.path, {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['minimum'], 16.0)

    def test_maximum_price_no_args(self):
        self.make_test_set()
        resp = self.c.get(self.path, {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['maximum'], 50.0)

    def test_average_price_no_args(self):
        self.make_test_set()
        resp = self.c.get(self.path, {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['average'], (16.0 + 18.0 + 50.0) / 3)

    def test_first_std_deviation_no_args(self):
        self.make_test_set()
        resp = self.c.get(self.path, {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.data['first_standard_deviation']), 15)

    def test_histogram_length(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'histogram': 5})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['wage_histogram']), 5)

    def test_histogram_not_numeric(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'histogram': 'x'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['wage_histogram']), 0)

    def test_histogram_bins(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'histogram': 2})
        self.assertEqual(resp.status_code, 200)
        self.assertResultsEqual(resp.data['wage_histogram'], [
          {'count': 2, 'min': 16.0, 'max': 33.0},
          {'count': 1, 'min': 33.0, 'max': 50.0}
        ])

    def test_filter_by_site(self):
        get_contract_recipe().make(_quantity=3, contractor_site=seq('Q'))
        resp = self.c.get(self.path, {'site': 'Q3'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC1233',
           'vendor_name': 'CompanyName3',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 8,
           'hourly_rate_year1': 23.0,
           'current_price': 23.0,
           'schedule': 'MOBIS',
           'contractor_site': 'Q3',
           'business_size': None}])

    def test_exclude_by_id(self):
        get_contract_recipe().make(id=100)
        get_contract_recipe().make(id=101)
        get_contract_recipe().make(id=102)

        resp = self.c.get(self.path, {'exclude': '102,100'})
        self.assertEqual(resp.status_code, 200)
        self.assertResultsEqual(resp.data['results'],
        [{
           'idv_piid': 'ABC1231',
           'vendor_name': 'CompanyName1',
           'labor_category': 'Business Analyst II',
           'schedule': 'MOBIS',
           'current_price': 21.00
        }])

    def make_test_set(self):
        mommy.make(
                Contract,
                id=1,
                idv_piid="ABC123",
                piid="123",
                vendor_name="ACME Corp.",
                labor_category="Legal Services",
                min_years_experience=10,
                hourly_rate_year1=18.00,
                current_price=18.00,
        )
        mommy.make(
                Contract,
                id=2,
                idv_piid="ABC234",
                piid="234",
                vendor_name="Numbers R Us",
                labor_category="Accounting, CPA",
                education_level='MA',
                min_years_experience=5,
                hourly_rate_year1=50.00,
                current_price=50.00,
        )
        mommy.make(
                Contract,
                id=3,
                idv_piid="ABC345",
                piid="345",
                vendor_name="Word Power Co.",
                labor_category="Writer/Editor",
                education_level='BA',
                min_years_experience=1,
                hourly_rate_year1=16.00,
                current_price=16.00,
        )

    def assertResultsEqual(self, results, expected, just_expected_fields=True):
        dict_results = [dict(x) for x in results]

        # test the right number of results is returned
        self.assertEqual(len(results), len(expected), "Got a different number of results than expected.")

        if 'idv_piid' in dict_results[0].keys():
            result_ids = [x['idv_piid'] for x in dict_results]
            expected_ids = [x['idv_piid'] for x in expected]

            # test the sort order
            # if the set of IDs returned are as expected,
            # then if the order is different, we can assume sorting is not working right
            # the resulting error message will actually show us how the ordering is wrong
            if set(result_ids) == set(expected_ids):
                self.assertEqual(result_ids, expected_ids, "The sort order is wrong!")

        if just_expected_fields:
            dict_results = [ { key: x[key] for key in expected[0].keys() } for x in dict_results ]

        for i, result in enumerate(dict_results):
            self.assertEqual(result, expected[i], "\n===== Object at index {} failed. =====".format(i))

    def prettyPrint(self, thing):
        """
        Pretty-printing for debugging purposes.
        """
        import pprint; pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(thing)
