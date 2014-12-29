DEBUG=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hourglass',
        'USER': '',
        'PASSWORD': '',
    }
}

SECRET_KEY = ''

# for front-end testing with Sauce
# if SAUCE is False, the front-end tests use PhantomJS locally
SAUCE = False
SAUCE_USERNAME = ''
SAUCE_ACCESS_KEY = ''
DOMAIN_TO_TEST = 'hourglass.18f.us'
