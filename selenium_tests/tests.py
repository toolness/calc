from django.conf import settings
from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

class FunctionalTests(LiveServerTestCase): 

    def setUp(self):
        if settings.SAUCE:
            self.base_url = "http://%s" % settings.DOMAIN_TO_TEST
            self.desired_capabilities = DesiredCapabilities.CHROME
            sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
            self.driver = webdriver.Remote(
                desired_capabilities=self.desired_capabilities,
                command_executor=sauce_url % (settings.SAUCE_USERNAME, settings.SAUCE_ACCESS_KEY)
            )
        else:
            self.base_url = 'http://localhost:8000'
            self.driver = webdriver.PhantomJS()

    def load(self, uri='/'):
        self.driver.get(self.base_url + uri)
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

    def test_titles_are_correct(self):
        driver = self.load()
        self.assertTrue(driver.title.startswith('Hourglass'), 'Title mismatch')

    def test_form_submit_loading(self):
        driver = self.load()
        self.search_for('Architect')
        form = self.submit_form()
        self.assertTrue(has_class(form, 'loading'), "Form doesn't have 'loading' class")
        wait_for(self.data_is_loaded)
        self.assertTrue(has_class(form, 'loaded'), "Form doesn't have 'loaded' class")
        self.assertFalse(has_class(form, 'loading'), "Form shouldn't have 'loading' class after loading")

    def test_search_input(self):
        driver = self.load()
        self.search_for('Engineer')
        self.submit_form()
        self.assertTrue('q=Engineer' in driver.current_url, 'Missing "q=Engineer" in query string')
        wait_for(self.data_is_loaded)

        results_count = driver.find_element_by_id('results-count').text
        self.assertTrue(results_count != u'...', 'Results count mismatch')
        labor_cell = driver.find_element_by_css_selector('tbody tr .column-labor_category')
        self.assertTrue('Engineer' in labor_cell.text, 'Labor category cell text mismatch')

    def test_price_filter(self):
        driver = self.load()
        form = self.get_form()
        set_form_value(form, 'price__gt', 100)
        self.submit_form()
        self.assertTrue('price__gt=100' in driver.current_url, 'Missing "price__gt=100" in query string')
        wait_for(self.data_is_loaded)

        price_cell = driver.find_element_by_css_selector('tbody tr .column-current_price')
        dollars = float(price_cell.text[1:])
        self.assertTrue(dollars > 100, 'Minimum price mismatch')

    def test_sort_columns(self):
        driver = self.load()
        form = self.get_form()

        # limit the result set so it loads more quickly
        self.search_for('Consultant')
        header = driver.find_element_by_css_selector('th.column-min_years_experience')

        header.click()
        self.submit_form()
        self.assertTrue('sort=min_years_experience' in driver.current_url, 'Missing "sort=min_years_experience" in query string')
        self.assertTrue(has_class(header, 'sorted'), "Header doesn't have 'sorted' class")
        self.assertFalse(has_class(header, 'descending'), "Header shouldn't have 'descending' class")

        wait_for(self.data_is_loaded, timeout=10)
        # iterate through all of the min_years_experience cells,
        # and ensure that they have a value >= the previous one
        value = 0
        for cell in driver.find_elements_by_css_selector('td.column-min_years_experience'):
            cell_value = int(cell.text)
            self.assertTrue(cell_value >= value, "%d < %d (not sorted)" % (cell_value, value))
            value = cell_value

        header.click()
        self.submit_form()
        self.assertTrue('sort=-min_years_experience' in driver.current_url, 'Missing "sort=-min_years_experience" in query string')
        self.assertTrue(has_class(header, 'sorted'), "Header doesn't have 'sorted' class")
        self.assertTrue(has_class(header, 'descending'), "Header doesn't have 'descending' class")

        wait_for(self.data_is_loaded, timeout=10)
        # iterate through all of the min_years_experience cells,
        # and ensure that they have a value <= the previous one
        value = 1000000
        for cell in driver.find_elements_by_css_selector('td.column-min_years_experience'):
            cell_value = int(cell.text)
            self.assertTrue(cell_value <= value, "%d > %d (not sorted)" % (cell_value, value))
            value = cell_value

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
