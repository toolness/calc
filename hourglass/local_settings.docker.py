DEBUG=True

SECRET_KEY = 'DOCKER DEVELOPMENT'

# for front-end testing with Sauce
REMOTE_TESTING = {
    'enabled': False,
    'hub_url': 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub',
    'username': '',
    'access_key': '',
    'capabilities': {
        # 'browser': 'internet explorer',
        # 'version': '9.0',
        # 'platform': 'Windows 7'
    }
}


SECURE_SSL_REDIRECT = False
