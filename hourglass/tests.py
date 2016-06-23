import unittest
import json
from django.test import TestCase as DjangoTestCase
from django.test import override_settings

from .settings_utils import load_cups_from_vcap_services


class RobotsTests(DjangoTestCase):
    @override_settings(ENABLE_SEO_INDEXING=False)
    def test_disable_seo_indexing_works(self):
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, b"User-agent: *\nDisallow: /")

    @override_settings(ENABLE_SEO_INDEXING=True)
    def test_enable_seo_indexing_works(self):
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, b"User-agent: *\nDisallow:")


class CupsTests(unittest.TestCase):
    @staticmethod
    def make_vcap_services_env(vcap_services):
        return {
            'VCAP_SERVICES': json.dumps(vcap_services)
        }

    def test_noop_if_vcap_services_not_in_env(self):
        env = {}
        load_cups_from_vcap_services('blah', env=env)
        self.assertEqual(env, {})

    def test_irrelevant_cups_are_ignored(self):
        env = self.make_vcap_services_env({
          "user-provided": [
            {
              "label": "user-provided",
              "name": "NOT-boop-env",
              "syslog_drain_url": "",
              "credentials": {
                "boop": "jones"
              },
              "tags": []
            }
          ]
        })

        load_cups_from_vcap_services('boop-env', env=env)

        self.assertFalse('boop' in env)

    def test_credentials_are_loaded(self):
        env = self.make_vcap_services_env({
          "user-provided": [
            {
              "label": "user-provided",
              "name": "boop-env",
              "syslog_drain_url": "",
              "credentials": {
                "boop": "jones"
              },
              "tags": []
            }
          ]
        })

        load_cups_from_vcap_services('boop-env', env=env)

        self.assertEqual(env['boop'], 'jones')
