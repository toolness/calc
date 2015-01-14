from django.conf import settings
from django.test import LiveServerTestCase
from itertools import cycle
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from contracts.mommy_recipes import get_contract_recipe
from model_mommy.recipe import seq

import time


class FunctionalTests(LiveServerTestCase):

    def setUp(self):
        if settings.SAUCE:
            self.live_server_url = "http://%s" % settings.DOMAIN_TO_TEST
            self.desired_capabilities = DesiredCapabilities.CHROME
            sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
            self.driver = webdriver.Remote(
                desired_capabilities=self.desired_capabilities,
                command_executor=sauce_url % (settings.SAUCE_USERNAME, settings.SAUCE_ACCESS_KEY)
            )
        else:
            self.driver = webdriver.PhantomJS()
            self.longMessage = True
            self.maxDiff = None
            super(FunctionalTests, self).setUp()

    def load(self, uri='/'):
        self.driver.get(self.live_server_url + uri)
        return self.driver

    def get_form(self):
        return self.driver.find_element_by_id('search')

    def submit_form(self):
        form = self.get_form()
        form.submit()
        return form

    def search_for(self, query):
        self.driver.find_element_by_name('q').send_keys(query)

    def data_is_loaded(self):
        form = self.get_form()
        if has_class(form, 'error'):
            raise Exception("Form submit error: '%s'" % form.find_element_by_css_selector('.error').text)
        return has_class(form, 'loaded')

    def test_results_count__empty_result_set(self):
        driver = self.load()
        self.assertEqual(driver.find_element_by_id('results-count').text, '0')

    def test_results_count(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Engineer"))
        driver = self.load()
        self.assertEqual(int(driver.find_element_by_id('results-count').text), 10)

    def test_titles_are_correct(self):
        get_contract_recipe().make(_quantity=1, labor_category=seq("Architect"))
        driver = self.load()
        wait_for(self.data_is_loaded)
        self.assertTrue(driver.title.startswith('Hourglass'), 'Title mismatch, {} does not start with Hourglass'.format(driver.title))

    def test_form_submit_loading(self):
        get_contract_recipe().make(_quantity=1, labor_category=seq("Architect"))
        self.load()
        self.search_for('Architect')
        form = self.submit_form()
        self.assertTrue(has_class(form, 'loading'), "Form doesn't have 'loading' class")
        wait_for(self.data_is_loaded)
        self.assertTrue(has_class(form, 'loaded'), "Form doesn't have 'loaded' class")
        self.assertFalse(has_class(form, 'loading'), "Form shouldn't have 'loading' class after loading")

    def test_search_input(self):
        get_contract_recipe().make(_quantity=9, labor_category=cycle(["Engineer", "Architect", "Writer"]))
        driver = self.load()
        self.search_for('Engineer')
        self.submit_form()
        self.assertTrue('q=Engineer' in driver.current_url, 'Missing "q=Engineer" in query string')

        results_count = driver.find_element_by_id('results-count').text
        self.assertEqual(int(results_count), 3, 'Results count mismatch.')
        labor_cell = driver.find_element_by_css_selector('tbody tr .column-labor_category')
        self.assertTrue('Engineer' in labor_cell.text, 'Labor category cell text mismatch')

    def test_price_gt(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(80, 10), current_price=seq(80, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        minimum = 100
        set_form_value(form, 'price__gt', minimum)
        self.submit_form()
        self.assertTrue(('price__gt=%d' % minimum) in driver.current_url, 'Missing "price__gt=%d" in query string' % minimum)

    def test_price_lt(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(80, 10), current_price=seq(80, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        maximum = 100
        set_form_value(form, 'price__lt', maximum)
        self.submit_form()
        self.assertTrue(('price__lt=%d' % maximum) in driver.current_url, 'Missing "price__lt=%d" in query string' % maximum)

    def test_sort_columns(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Consultant"), hourly_rate_year1=seq(80, 10), current_price=seq(80, 10))
        driver = self.load()
        self.get_form()

        header = driver.find_element_by_css_selector('th.column-min_years_experience')

        header.click()
        self.submit_form()
        self.assertTrue('sort=min_years_experience' in driver.current_url, 'Missing "sort=min_years_experience" in query string')
        self.assertTrue(has_class(header, 'sorted'), "Header doesn't have 'sorted' class")
        self.assertFalse(has_class(header, 'descending'), "Header shouldn't have 'descending' class")

        header.click()
        self.submit_form()
        self.assertTrue('sort=-min_years_experience' in driver.current_url, 'Missing "sort=-min_years_experience" in query string')
        self.assertTrue(has_class(header, 'sorted'), "Header doesn't have 'sorted' class")
        self.assertTrue(has_class(header, 'descending'), "Header doesn't have 'descending' class")


def wait_for(condition, timeout=3):
    start = time.time()
    while time.time() < start + timeout:
        if condition():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(condition.__name__))


def has_class(element, klass):
    return klass in element.get_attribute('class').split(' ')


def set_select_value(select, value):
    select.click()
    for option in select.find_elements_by_tag_name('option'):
        if option.get_attribute('value') == value:
            option.click()


def set_form_value(form, key, value):
    field = form.find_element_by_name(key)
    if field.tag_name == 'select':
        set_select_value(field, value)
    else:
        field_type = field.get_attribute('type')
        if field_type in ('checkbox', 'radio'):
            if field.get_attribute('value') == value:
                field.click()
        else:
            field.send_keys(value)
    return field


def set_form_values(self, values):
    for key, value in values.entries():
        set_form_value(key, value)

if __name__ == '__main__':
    import unittest
    unittest.main()
