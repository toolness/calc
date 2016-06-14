DEBUG = True

from django.utils.crypto import get_random_string

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hourglass',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}

SECRET_KEY = get_random_string(50)

SECURE_SSL_REDIRECT = False
