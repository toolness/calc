from django.test import TestCase
from contracts.mommy_recipes import get_contract_recipe
from itertools import cycle


class ContractTestCase(TestCase):

    def test_readable_business_size(self):
        business_sizes = ('O', 'S')
        contract1, contract2 = get_contract_recipe().make(_quantity=2, business_size=cycle(business_sizes))
        self.assertEqual(contract1.get_readable_business_size(), 'other than small business')
        self.assertEqual(contract2.get_readable_business_size(), 'small business')

    def test_get_education_code(self):
        c = get_contract_recipe().make()
        self.assertEqual(c.get_education_code('Bachelors'), 'BA')
        self.assertIsNone(c.get_education_code('Nursing'), None)

    def test_normalize_rate(self):
        c = get_contract_recipe().make()
        self.assertEqual(c.normalize_rate('$1,000.00,'), 1000.0)
