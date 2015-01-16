from django.conf import settings
from django.test import LiveServerTestCase
from itertools import cycle
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from contracts.mommy_recipes import get_contract_recipe
from model_mommy.recipe import seq

import re
import time


class FunctionalTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.PhantomJS()
        cls.longMessage = True
        cls.maxDiff = None
        super(FunctionalTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        if settings.SAUCE:
            self.live_server_url = "http://%s" % settings.DOMAIN_TO_TEST
            self.desired_capabilities = DesiredCapabilities.CHROME
            sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
            self.driver = webdriver.Remote(
                desired_capabilities=self.desired_capabilities,
                command_executor=sauce_url % (settings.SAUCE_USERNAME, settings.SAUCE_ACCESS_KEY)
            )

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
        self.assertResultsCount(driver, 0)

    def test_results_count(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Engineer"))
        driver = self.load()
        self.assertResultsCount(driver, 10)

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
        wait_for(self.data_is_loaded)

        self.assertResultsCount(driver, 3)
        labor_cell = driver.find_element_by_css_selector('tbody tr .column-labor_category')
        self.assertTrue('Engineer' in labor_cell.text, 'Labor category cell text mismatch')

    def test_price_gte(self):
        # note: the hourly rates here will actually start at 80-- this seems like a bug, but whatever
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(70, 10), current_price=seq(70, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        minimum = 100
        # add results count check
        set_form_value(form, 'price__gte', minimum)
        self.submit_form()
        wait_for(self.data_is_loaded)
        self.assertResultsCount(driver, 8)
        self.assertTrue(('price__gte=%d' % minimum) in driver.current_url, 'Missing "price__gte=%d" in query string' % minimum)

    def test_price_lte(self):
        # note: the hourly rates here will actually start at 80-- this seems like a bug, but whatever
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(70, 10), current_price=seq(70, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        maximum = 100
        # add results count check
        set_form_value(form, 'price__lte', maximum)
        self.submit_form()
        wait_for(self.data_is_loaded)
        self.assertResultsCount(driver, 3)
        self.assertTrue(('price__lte=%d' % maximum) in driver.current_url, 'Missing "price__lte=%d" in query string' % maximum)

    def test_price_range(self):
        # note: the hourly rates here will actually start at 80-- this seems like a bug, but whatever
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(70, 10), current_price=seq(70, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        minimum = 100
        maximum = 130
        set_form_value(form, 'price__gte', minimum)
        set_form_value(form, 'price__lte', maximum)
        self.submit_form()
        wait_for(self.data_is_loaded)
        self.assertResultsCount(driver, 4)
        self.assertTrue(('price__gte=%d' % minimum) in driver.current_url, 'Missing "price__gte=%d" in query string' % minimum)
        self.assertTrue(('price__lte=%d' % maximum) in driver.current_url, 'Missing "price__lte=%d" in query string' % maximum)

    def test_sort_columns(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Consultant"), hourly_rate_year1=seq(80, 10), current_price=seq(80, 10))
        driver = self.load()
        self.get_form()

        header = find_column_header(driver, 'min_years_experience')

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

    def test_there_is_no_business_size_column(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"), business_size='o')
        driver = self.load()
        form = self.get_form()

        col_headers = get_column_headers(driver)

        for head in col_headers:
            self.assertFalse(has_matching_class(head, 'column-business[_-]size'))

    def test_filter_to_only_small_businesses(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"), business_size='o')
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Small Biz"), business_size='s')
        driver = self.load()
        form = self.get_form()

        set_form_value(form, 'business_size', 's')
        self.submit_form()

        wait_for(self.data_is_loaded)
        self.assertResultsCount(driver, 5)

        self.assertIsNone(re.search(r'Large Biz\d+', driver.page_source))
        self.assertIsNotNone(re.search(r'Small Biz\d+', driver.page_source))

    def test_filter_to_only_large_businesses(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"), business_size='o')
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Small Biz"), business_size='s')
        driver = self.load()
        form = self.get_form()

        set_form_value(form, 'business_size', 'o')
        self.submit_form()

        wait_for(self.data_is_loaded)
        self.assertResultsCount(driver, 5)

        self.assertIsNone(re.search(r'Small Biz\d+', driver.page_source))
        self.assertIsNotNone(re.search(r'Large Biz\d+', driver.page_source))

    def test_no_filter_shows_all_sizes_of_business(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"), business_size='o')
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Small Biz"), business_size='s')
        driver = self.load()

        self.assertResultsCount(driver, 10)

        self.assertIsNotNone(re.search(r'Small Biz\d+', driver.page_source))
        self.assertIsNotNone(re.search(r'Large Biz\d+', driver.page_source))

    def test_schedule_column_is_collapsed_by_default(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load()
        col_header = find_column_header(driver, 'schedule')

        self.assertTrue(has_class(col_header, 'collapsed'))

    def test_unhide_schedule_column(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load()
        col_header = find_column_header(driver, 'schedule')

        # unhide column
        col_header.click()

        self.assertFalse(has_class(col_header, 'collapsed'))

    def test_schedule_column_is_last(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load()
        col_headers = get_column_headers(driver)

        self.assertTrue(has_class(col_headers[-1], 'column-schedule'))

    def test_schedule_column_is_sortable(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load()
        col_header = find_column_header(driver, 'schedule')

        self.assertTrue(has_class(col_header, 'sortable'))

    def assertResultsCount(self, driver, num):
        self.assertEqual(int(driver.find_element_by_id('results-count').text), num)


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

def has_matching_class(element, regex):
    return re.search(regex, element.get_attribute('class'))

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


def set_form_values(values):
    for key, value in values.entries():
        set_form_value(key, value)

def find_column_header(driver, col_name):
    return driver.find_element_by_css_selector('th.column-{}'.format(col_name))

def get_column_headers(driver):
    return driver.find_elements_by_xpath('//thead/tr/th')



if __name__ == '__main__':
    import unittest
    unittest.main()
