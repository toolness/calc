from django.test import TestCase, Client
from model_mommy import mommy
from contracts.models import Contract

class ContractsTest(TestCase):
    """ tests for the /api/rates endpoint """

    def setUp(self):
        self.c = Client()
        self.path = '/api/rates/'
        self.contract_legal = mommy.make(
                Contract,
                idv_piid="ABC123",
                piid="123",
                vendor_name="ACME Corp.",
                labor_category="Legal Services",
                min_years_experience=5,
                hourly_rate_year1=18.00,
                current_price=18.00,
        )
        self.contract_accounting = mommy.make(
                Contract,
                idv_piid="ABC234",
                piid="234",
                vendor_name="Numbers R Us",
                labor_category="Accounting, CPA",
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
                min_years_experience=5,
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
           'education_level': None,
           'min_years_experience': 5,
           'hourly_rate_year1': 50.0,
           'current_price': 50.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def test_filter_by_price__exact(self):
        resp = self.c.get(self.path, {'price': 18})
        self.assertEqual(resp.status_code, 200)

        self.assertResultsEqual(resp.data['results'],
         [{'idv_piid': 'ABC123',
           'vendor_name': 'ACME Corp.',
           'labor_category': 'Legal Services',
           'education_level': None,
           'min_years_experience': 5,
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
           'education_level': None,
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
           'labor_category': 'Writing/Editing',
           'education_level': None,
           'min_years_experience': 4,
           'hourly_rate_year1': 16.0,
           'current_price': 16.0,
           'schedule': None,
           'contractor_site': None,
           'business_size': None}])

    def assertResultsEqual(self, results, expected):
        dict_results = [dict(x) for x in results]
        for i, result in enumerate(results):
            try:
                self.assertEqual(result, expected[i], 'Items at index {} did not match'.format(i))
            except Exception as e:
                print(e)
