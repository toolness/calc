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
        # cls.driver = webdriver.Firefox()
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

    def load_and_wait(self, uri='/'):
        self.load(uri)
        wait_for(self.data_is_loaded)
        return self.driver

    def get_form(self):
        return self.driver.find_element_by_id('search')

    def submit_form(self):
        form = self.get_form()
        form.submit()
        return form

    def submit_form_and_wait(self):
        form = self.submit_form()
        wait_for(self.data_is_loaded)
        return form

    def search_for(self, query):
        self.driver.find_element_by_name('q').send_keys(query)

    def data_is_loaded(self):
        form = self.get_form()
        if has_class(form, 'error'):
            raise Exception("Form submit error: '%s'" % form.find_element_by_css_selector('.error').text)
        return has_class(form, 'loaded')

    def test_results_count__empty_result_set(self):
        driver = self.load_and_wait()
        self.assertResultsCount(driver, 0)

    def test_results_count(self):
        get_contract_recipe().make(_quantity=10, labor_category=seq("Engineer"))
        driver = self.load_and_wait()
        self.assertResultsCount(driver, 10)

    def test_titles_are_correct(self):
        get_contract_recipe().make(_quantity=1, labor_category=seq("Architect"))
        driver = self.load_and_wait()
        self.assertTrue(driver.title.startswith('Hourglass'), 'Title mismatch, {} does not start with Hourglass'.format(driver.title))

    def test_filter_order_is_correct(self):
        get_contract_recipe().make(_quantity=1, labor_category=seq("Architect"))
        driver = self.load()
        form = self.get_form()

        inputs = form.find_elements_by_css_selector("input:not([type='hidden'])")

        # the last visible form inputs should be the price filters
        self.assertEqual(inputs[-2].get_attribute('name'), 'price__gte')
        self.assertEqual(inputs[-1].get_attribute('name'), 'price__lte')

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
        # note: the hourly rates here will actually start at 80-- this seems
        # like a bug, but whatever
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(70, 10), current_price=seq(70, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        minimum = 100
        # add results count check
        set_form_value(form, 'price__gte', minimum)
        self.submit_form_and_wait()
        self.assertTrue(('price__gte=%d' % minimum) in driver.current_url, 'Missing "price__gte={0}" in query string: {1}'.format(minimum, driver.current_url))
        self.assertResultsCount(driver, 8)

    def test_price_lte(self):
        # note: the hourly rates here will actually start at 80-- this seems
        # like a bug, but whatever
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(70, 10), current_price=seq(70, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        maximum = 100
        # add results count check
        set_form_value(form, 'price__lte', maximum)
        self.submit_form_and_wait()
        self.assertTrue(('price__lte=%d' % maximum) in driver.current_url, 'Missing "price__lte=%d" in query string' % maximum)
        self.assertResultsCount(driver, 3)

    def test_price_range(self):
        # note: the hourly rates here will actually start at 80-- this seems
        # like a bug, but whatever
        get_contract_recipe().make(_quantity=10, labor_category=seq("Contractor"), hourly_rate_year1=seq(70, 10), current_price=seq(70, 10))
        driver = self.load()
        form = self.get_form()
        self.search_for('Contractor')

        minimum = 100
        maximum = 130
        set_form_value(form, 'price__gte', minimum)
        set_form_value(form, 'price__lte', maximum)
        self.submit_form_and_wait()
        self.assertResultsCount(driver, 4)
        self.assertTrue(('price__gte=%d' % minimum) in driver.current_url, 'Missing "price__gte=%d" in query string' % minimum)
        self.assertTrue(('price__lte=%d' % maximum) in driver.current_url, 'Missing "price__lte=%d" in query string' % maximum)

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
        driver = self.load_and_wait()
        form = self.get_form()

        set_form_value(form, 'business_size', 's')
        self.submit_form_and_wait()

        self.assertResultsCount(driver, 5)

        self.assertIsNone(re.search(r'Large Biz\d+', driver.page_source))
        self.assertIsNotNone(re.search(r'Small Biz\d+', driver.page_source))

    def test_filter_to_only_large_businesses(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"), business_size='o')
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Small Biz"), business_size='s')
        driver = self.load_and_wait()
        form = self.get_form()

        set_form_value(form, 'business_size', 'o')
        self.submit_form_and_wait()

        self.assertResultsCount(driver, 5)

        self.assertIsNone(re.search(r'Small Biz\d+', driver.page_source))
        self.assertIsNotNone(re.search(r'Large Biz\d+', driver.page_source))

    def test_no_filter_shows_all_sizes_of_business(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"), business_size='o')
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Small Biz"), business_size='s')
        driver = self.load_and_wait()

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

        # un-hide column
        col_header.find_element_by_css_selector('.toggle-collapse').click()

        self.assertFalse(has_class(col_header, 'collapsed'))

        # re-hide column
        col_header.find_element_by_css_selector('.toggle-collapse').click()

        self.assertTrue(has_class(col_header, 'collapsed'))

    def test_schedule_column_is_last(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        col_headers = get_column_headers(driver)
        self.assertTrue(has_class(col_headers[-1], 'column-schedule'))

    def test_sortable_columns__non_default(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()

        for col in ['schedule', 'labor_category', 'education_level', 'min_years_experience']:
            self._test_column_is_sortable(driver, col)

    def _test_column_is_sortable(self, driver, colname):
        col_header = find_column_header(driver, colname)
        self.assertTrue(has_class(col_header, 'sortable'), "{} column is not sortable".format(colname))
        # NOT sorted by default
        self.assertFalse(has_class(col_header, 'sorted'), "{} column is sorted by default".format(colname))
        col_header.click()
        self.assertTrue(has_class(col_header, 'sorted'), "{} column is not sorted after clicking".format(colname))

    def test_price_column_is_sortable_and_is_the_default_sort(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        col_header = find_column_header(driver, 'current_price')
        # current_price should be sorted ascending by default
        self.assertTrue(has_class(col_header, 'sorted'), "current_price is not the default sort")
        self.assertTrue(has_class(col_header, 'sortable'), "current_price column is not sortable")
        self.assertFalse(has_class(col_header, 'descending'), "current_price column is descending by default")
        col_header.click()
        self.assertTrue(has_class(col_header, 'sorted'), "current_price is still sorted after clicking")

    def test_one_column_is_sortable_at_a_time(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        header1 = find_column_header(driver, 'education_level')
        header2 = find_column_header(driver, 'labor_category')

        header1.click()
        self.assertTrue(has_class(header1, 'sorted'), "column 1 is not sorted")
        self.assertFalse(has_class(header2, 'sorted'), "column 2 is still sorted (but should not be)")

        header2.click()
        self.assertTrue(has_class(header2, 'sorted'), "column 2 is not sorted")
        self.assertFalse(has_class(header1, 'sorted'), "column 1 is still sorted (but should not be)")

    def test_histogram_is_shown(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        rect_count = len(driver.find_elements_by_css_selector('.histogram rect'))
        self.assertTrue(rect_count > 0, "No histogram rectangles found (selector: '.histogram rect')")

    def test_histogram_shows_min_max(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        histogram = driver.find_element_by_css_selector('.histogram')
        for metric in ('min', 'max', 'average'):
            node = histogram.find_element_by_class_name(metric)
            self.assertTrue(node.text.startswith(u'$'), "histogram '.%s' node does not start with '$': '%s'" % (metric, node.text))

    def test_histogram_shows_intevals(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        ticks = driver.find_elements_by_css_selector('.histogram .x.axis .tick')
        # XXX there should be 10 bins, but 11 labels (one for each bin edge)
        self.assertEqual(len(ticks), 11, "Found wrong number of x-axis ticks: %d" % len(ticks))

    def test_histogram_shows_tooltips(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        bars = driver.find_elements_by_css_selector('.histogram .bar')
        # TODO: check for "real" tooltips?
        for i, bar in enumerate(bars):
            title = bar.find_element_by_css_selector('title')
            self.assertIsNotNone(title.text, "Histogram bar #%d has no text" % i)

    def assertResultsCount(self, driver, num):
        results_count = driver.find_element_by_id('results-count').text
        # remove commas from big numbers (e.g. "1,000" -> "1000")
        results_count = results_count.replace(',', '')
        self.assertNotEqual(results_count, u'', "No results count")
        self.assertEqual(results_count, str(num), "Results count mismatch: '%s' != %d" % (results_count, num))


def wait_for(condition, timeout=3):
    start = time.time()
    while time.time() < start + timeout:
        if condition():
            return True
        else:
            time.sleep(0.05)
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
            field.send_keys(str(value))
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
