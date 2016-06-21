DEBUG=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hourglass',
        'USER': '',
        'PASSWORD': '',
    }
}

SECRET_KEY = 'I am an insecure secret key intended ONLY for dev/testing.'

SECURE_SSL_REDIRECT = False
