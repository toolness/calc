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

    def test_titles_are_correct(self):
        driver = self.driver
        driver.get(self.base_url + '/')
        self.assertTrue(driver.title.startswith('Hourglass'))

if __name__ == '__main__':
    import unittest
    unittest.main()
