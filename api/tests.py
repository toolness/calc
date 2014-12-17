from django.test import TestCase, Client

class ContractsTest(TestCase):
    """ tests for the /api/rates endpoint """
    fixtures = ['contracts.json']

    def setUp(self):
        self.c = Client()
        self.path = '/api/rates/'

    def test_empty_results(self):
        resp = self.c.get(self.path, {'q': 'nsfr87y3487h3rufbf'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'], [])
