from django.test import TestCase, Client
from model_mommy import mommy
from contracts.models import Contract
from api.mommy_recipes import contract_recipe

class ContractsTest(TestCase):
    """ tests for the /api/rates endpoint """

    def setUp(self):
        self.maxDiff=None

        self.c = Client()
        self.path = '/api/rates/'
        self.contract_legal = mommy.make(
                Contract,
                idv_piid="ABC123",
                piid="123",
                vendor_name="ACME Corp.",
                labor_category="Legal Services",
                min_years_experience=10,
                hourly_rate_year1=18.00,
                current_price=18.00,
        )
        self.contract_accounting = mommy.make(
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
        self.contract_writing = mommy.make(
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

    def test_empty_results(self):
        resp = self.c.get(self.path, {'q': 'nsfr87y3487h3rufbf'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_search_results(self):
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
        resp = self.c.get(self.path, {'q': 'legal advice'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])

    def test_filter_by_price__exact(self):
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
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 6,
           'hourly_rate_year1': 21.0,
           'current_price': 21.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None},
         {'idv_piid': 'ABC1233',
           'vendor_name': 'CompanyName3',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 8,
           'hourly_rate_year1': 23.0,
           'current_price': 23.0,
           'schedule': 'MOBIS',
           'contractor_site': None,
           'business_size': None}])


    def assertResultsEqual(self, results, expected):
        dict_results = [dict(x) for x in results]
        self.assertEqual(len(results), len(expected))
        for i, result in enumerate(results):
            self.assertEqual(dict(result), expected[i])
