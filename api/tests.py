from django.test import TestCase, Client
from model_mommy import mommy
from model_mommy.recipe import seq
from contracts.models import Contract
from contracts.mommy_recipes import contract_recipe
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

    def test_empty_results(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'nsfr87y3487h3rufbf'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_search_results(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'q': 'accounting'})
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.data['results'],
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

        self.assertEqual(resp.data['results'],
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

    def test_filter_by_price__gt(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price__gt': 18})
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

    def test_filter_by_price__lt(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price__lt': 18})
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

    def test_filter_by_price__gt_and_lt(self):
        self.make_test_set()
        resp = self.c.get(self.path, {'price__lt': 20, 'price__gt': 16})
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
        self.make_test_set()
        resp = self.c.get(self.path, {'min_education': 'MA'})
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

    def test_filter_by_schedule(self):
        contract_recipe.make(_quantity=3)
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
        contract_recipe.make(_quantity=3, business_size=cycle(self.BUSINESS_SIZES))
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
        contract_recipe.make(vendor_name='Numbers R Us')

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
         {'idv_piid': 'ABC1234',
           'vendor_name': 'Numbers R Us',
           'labor_category': 'Business Analyst II',
           'education_level': None,
           'min_years_experience': 9,
           'hourly_rate_year1': 24.0,
           'current_price': 24.0,
           'schedule': 'PES',
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
        self.assertEqual(len(resp.data['wage_histogram']), 2)
        self.assertResultsEqual(resp.data['wage_histogram'], [
          {'count': 2, 'min': 16.0, 'max': 33.0},
          {'count': 1, 'min': 33.0, 'max': 50.0}
        ])

    def test_filter_by_site(self):
        contract_recipe.make(_quantity=3, contractor_site=seq('Q'))
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

    def make_test_set(self):
        mommy.make(
                Contract,
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
                idv_piid="ABC345",
                piid="345",
                vendor_name="Word Power Co.",
                labor_category="Writer/Editor",
                education_level='BA',
                min_years_experience=1,
                hourly_rate_year1=16.00,
                current_price=16.00,
        )

    def assertResultsEqual(self, results, expected):
        dict_results = [dict(x) for x in results]
        self.assertEqual(len(results), len(expected))
        for i, result in enumerate(results):
            self.assertEqual(dict(result), expected[i], "\n===== Object at index {} failed. =====".format(i))
